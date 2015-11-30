//
//  pypyjs:  an experimental in-browser python environment.
//

(function() {

// Expose the main pypyjs function at global scope for this file,
// as well as in any module exports or 'window' object we can find.
if (this) {
  this.pypyjs = pypyjs;
}
if (typeof window !== "undefined") {
  window.pypyjs = pypyjs;
}
if (typeof module !== "undefined") {
  if (typeof module.exports !== "undefined") {
    module.exports = pypyjs;
  }
}


// Generic debugging printf.
var debug = function(){};
if (typeof console !== "undefined") {
  debug = console.log.bind(console);
} else if (typeof print !== "undefined" && typeof window === "undefined") {
  debug = print;
}


// Find the directory containing this very file.
// It can be quite difficult depending on execution environment...
if (typeof __dirname === "undefined" || true) {
  var __dirname = "./";
  // A little hackery to find the URL of this very file.
  // Throw an error, then parse the stack trace looking for filenames.
  var errlines = (new Error()).stack.split("\n");
  for (var i = 0; i < errlines.length; i++) {
    var match = /(at Anonymous function \(|at |@)(.+\/)pypyjs.js/.exec(errlines[i]);
    if (match) {
      __dirname = match[2];
      break;
    }
  }
}
if (__dirname.charAt(__dirname.length - 1) !== "/") {
  __dirname += "/";
}


if (typeof Promise === "undefined") {
  var Promise = require('es6-promise').Promise;
}


// Ensure we have reference to a 'FunctionPromise' constructor.
var FunctionPromise = require("./FunctionPromise.js");

if (typeof FunctionPromise === "undefined") {
  throw "FunctionPromise object not found";
}


// Create functions for handling default stdio streams.
// These will be shared by all VM instances by default.
//
// We default stdout and stderr to process outputs if available,
// printing/logging functions otherwise, and /dev/null if nothing
// else is available.  Unfortunately there's no good way to read
// synchronously from stdin in javascript, so that's always /dev/null.

var devNull = {
  stdin: function() { return null; },
  stdout: function() { },
  stderr: function() { }
}

var stdio = {
  stdin: null,
  stdout: null,
  stderr: null
}

stdio.stdin = devNull.stdin;

if (typeof process !== "undefined") {
  if (typeof process.stdout !== "undefined") {
    stdio.stdout = function(x) { process.stdout.write(x); }
  }
  if (typeof process.stderr !== "undefined") {
    stdio.stderr = function(x) { process.stderr.write(x); }
  }
}

var _print, _printErr;
if (typeof window === "undefined") {
  // print, printErr from v8, spidermonkey
  if (typeof print !== "undefined") {
    _print = print;
  }
  if (typeof printErr !== "undefined") {
    _printErr = printErr;
  }
}
if (typeof console !== "undefined") {
  if (typeof _print === "undefined") {
    _print = console.log.bind(console);
  }
  if (typeof _printErr === "undefined") {
    _printErr = console.error.bind(console);
  }
}

if (stdio.stdout == null && typeof _print !== "undefined") {
  // print()/console.log() will add a newline, so we buffer until we
  // receive one and then let it add it for us.
  stdio.stdout = (function() {
    var buffer = [];
    return function(data) {
      for (var i = 0; i < data.length; i++) {
        var x = data.charAt(i);
        if (x !== "\n") {
          buffer.push(x);
        } else {
          _print(buffer.join(""));
          buffer.splice(undefined, buffer.length);
        }
      }
    }
  })();
}

if (stdio.stderr == null && typeof _printErr !== "undefined") {
  // printErr()/console.error() will add a newline, so we buffer until we
  // receive one and then let it add it for us.
  stdio.stderr = (function() {
    var buffer = [];
    return function(data) {
      for (var i = 0; i < data.length; i++) {
        var x = data.charAt(i);
        if (x !== "\n") {
          buffer.push(x);
        } else {
          _printErr(buffer.join(""));
          buffer.splice(undefined, buffer.length);
        }
      }
    }
  })();
}

if (stdio.stdout === null) {
  stdio.stdout = devNull.stdout;
}

if (stdio.stderr === null) {
  stdio.stderr = devNull.stderr;
}

function pypyjs(opts) {

  opts = opts || {};
  this.rootURL = opts.rootURL;
  this.totalMemory = opts.totalMemory || 128 * 1024 * 1024;
  this.autoLoadModules = opts.autoLoadModules || true;
  this._pendingModules = {};
  this._loadedModules = {};
  this._allModules = {};

  // Allow opts to override default IO streams.
  this.stdin = opts.stdin || stdio.stdin;
  this.stdout = opts.stdout || stdio.stdout;
  this.stderr = opts.stderr || stdio.stderr;

  // Default to finding files relative to this very file.
  if (!this.rootURL && !pypyjs.rootURL) {
    pypyjs.rootURL = __dirname;
  }
  if (this.rootURL && this.rootURL.charAt(this.rootURL.length - 1) !== "/") {
    this.rootURL += "/";
  } 

  // If we haven't already done so, fetch and load the code for the VM.
  // We do this once and cache the result for re-use, so that we don't
  // have to pay asmjs compilation overhead each time we create the VM.

  if (! pypyjs._vmBuilderPromise) {
    pypyjs._vmBuilderPromise = this.fetch("pypyjs.vm.js").then((function(xhr) {
      // Parse the compiled code, hopefully asynchronously.
      // Unfortunately our use of Function constructor here doesn't
      // play very well with nodejs, where things like 'module' and
      // 'require' are not in the global scope.  We have to pass them
      // in explicitly as arguments.
      var funcBody = [
        // This is the compiled code for the VM.
        xhr.responseText,
        '\n',
        // Ensure that some functions are available on the Module,
        // for linking with jitted code.
        'if (!Module._jitInvoke && typeof _jitInvoke !== "undefined") {',
        '  Module._jitInvoke = _jitInvoke;',
        '}',
        // Keep some functions that are not exported by default, but
        // which appear in this scope when evaluating the above.
        "Module._emjs_make_handle = _emjs_make_handle;",
        "Module._emjs_free = _emjs_free;",
        // Call dependenciesFulfilled if it won't be done automatically.
        "dependenciesFulfilled=function() { inDependenciesFulfilled(FS); };",
        "if(!memoryInitializer||(!ENVIRONMENT_IS_WEB&&!ENVIRONMENT_IS_WORKER))dependenciesFulfilled();",
      ].join("");
      return FunctionPromise("Module", "inDependenciesFulfilled", "require",
                             "module", "__filename", "__dirname", funcBody)
    }).bind(this));
  }

  // Create a new instance of the compiled VM, bound to local state
  // and a local Module object.

  this._ready = new Promise((function(resolve, reject) {

    // Initialize the Module object.
    // We make it available on this object so that we can use
    // its methods to execute code in the VM.
    var Module = {};
    this._module = Module;
    Module.TOTAL_MEMORY = this.totalMemory;

    // We will set up the filesystem manually when we're ready.
    Module.noFSInit = true;
    Module.thisProgram = "/lib/pypyjs/pypyjs.js";
    Module.filePackagePrefixURL = this.rootURL || pypyjs.rootURL;
    Module.memoryInitializerPrefixURL = this.rootURL || pypyjs.rootURL;
    Module.locateFile = function(name) {
      return (this.rootURL || pypyjs.rootURL) + name;
    }

    // Don't start or stop the program, just set it up.
    // We'll call the API functions ourself.
    Module.noInitialRun = true;
    Module.noExitRuntime = true;

    // Route stdin to an overridable method on the object.
    var stdin = (function stdin() {
      return this.stdin();
    }).bind(this);
 
    // Route stdout to an overridable method on the object.
    // We buffer the output for efficiency.
    var stdout_buffer = []
    var stdout = (function stdout(x) {
      var c = String.fromCharCode(x);
      stdout_buffer.push(c);
      if (c === "\n" || stdout_buffer.length >= 128) {
        this.stdout(stdout_buffer.join(""));
        stdout_buffer = [];
      }
    }).bind(this);

    // Route stderr to an overridable method on the object.
    // We do not buffer stderr.
    var stderr = (function stderr(x) {
      var c = String.fromCharCode(x);
      this.stderr(c);
    }).bind(this);

    // This is where execution will continue after loading
    // the memory initialization data, if any.
    var initializedResolve, initializedReject;
    var initializedP = new Promise(function(resolve, reject) {
      initializedResolve = resolve;
      initializedReject = reject;
    });
    var FS;
    var dependenciesFulfilled = function(fs) {
      FS = fs;
      // Initialize the filesystem state.
      try {
        FS.init(stdin, stdout, stderr);
        Module.FS_createPath("/", "lib/pypyjs/lib_pypy", true, false);
        Module.FS_createPath("/", "lib/pypyjs/lib-python/2.7", true, false);
        initializedResolve();
      } catch (err) {
        initializedReject(err);
      }
    }
 
    // Begin fetching the metadata for available python modules.
    // With luck these can download while we jank around compiling
    // all of that javascript.
    // XXX TODO: also load memory initializer this way.
    var moduleDataP = this.fetch("modules/index.json");

    pypyjs._vmBuilderPromise.then((function(vmBuilder) {
      var args = [
        Module,
        dependenciesFulfilled,
        typeof undefined,
        typeof undefined,
        typeof undefined,
        typeof __dirname
      ];
      // This links the async-compiled module into our Module object.
      vmBuilder.apply(null, args);
      return initializedP;
    }).bind(this)).then((function() {
      // Continue with processing the downloaded module metadata.
      return moduleDataP.then((function(xhr) {
        // Store the module index, and load any preload modules.
        var modIndex = JSON.parse(xhr.responseText);
        this._allModules = modIndex.modules;
        if (modIndex.preload) {
          for (var name in modIndex.preload) {
            this._writeModuleFile(name, modIndex.preload[name]);
          }
        }
        // It's finally safe to launch the VM.
        Module.run();
        Module._rpython_startup_code();
        var pypy_home = Module.intArrayFromString("/lib/pypyjs/pypyjs.js");
        pypy_home = Module.allocate(pypy_home, 'i8', Module.ALLOC_NORMAL);
        Module._pypy_setup_home(pypy_home, 0);
        Module._free(pypy_home);
        var initCode = [
          "import js",
          "import sys; sys.platform = 'js'",
          "import traceback",
          "top_level_scope = {'__name__': '__main__'}"
        ];
        initCode.forEach(function(codeStr) {
          var code = Module.intArrayFromString(codeStr);
          var code = Module.allocate(code, 'i8', Module.ALLOC_NORMAL);
          if (!code) {
            throw new pypyjs.Error('Failed to allocate memory');
          }
          var res = Module._pypy_execute_source(code);
          if (res < 0) {
            throw new pypyjs.Error('Failed to execute python code');
          }
          Module._free(code);
        });
      }).bind(this))
    }).bind(this))
    .then(resolve, reject);
  }).bind(this));

};


// A simple file-fetching wrapper around XMLHttpRequest,
// that treats paths as relative to the pypyjs.js root url.
//
pypyjs.prototype.fetch = function (relpath, responseType) {
  if (typeof window === "undefined") {
    var localStorage = false;
  }
  else {
    var localStorage = window.localStorage;
  }
  var use_cache = pypyjs.cacheKey && localStorage && relpath != "pypyjs.vm.js";
  if (use_cache) {
    var item = localStorage.getItem(pypyjs.cacheKey+':'+relpath);
    if (item) {
      return new Promise((function(resolve, reject) {
        resolve({ responseText: item });
      }))
    }
  }
  // For the web, use XMLHttpRequest.
  if (typeof XMLHttpRequest !== "undefined") {
    return new Promise((function(resolve, reject) {
      var xhr = new XMLHttpRequest();
      xhr.onload = function() {
        if (xhr.status >= 400) {
          reject(xhr)
        } else {
          if (use_cache && xhr.responseText) {
            localStorage.setItem(pypyjs.cacheKey+':'+relpath, xhr.responseText);
          }
          resolve(xhr);
        }
      };
      var rootURL = this.rootURL || pypyjs.rootURL;
      xhr.open('GET', rootURL + relpath, true);
      xhr.responseType = responseType || "text";
      xhr.send(null);
    }).bind(this));
  }
  // For nodejs, use fs.readFile.
  if (typeof fs !== "undefined" && typeof fs.readFile !== "undefined") {
    return new Promise((function(resolve, reject) {
      var rootURL = this.rootURL || pypyjs.rootURL;
      fs.readFile(path.join(rootURL, relpath), function(err, data) {
        if (err) return reject(err);
        resolve({ responseText: data.toString() });
      });
    }).bind(this));
  }
  // For spidermonkey, use snarf (which has a binary read mode).
  if (typeof snarf !== "undefined") {
    return new Promise((function(resolve, reject) {
      var rootURL = this.rootURL || pypyjs.rootURL;
      var data = snarf(rootURL + relpath);
      resolve({ responseText: data });
    }).bind(this));
  }
  // For d8, use read() and readbuffer().
  if (typeof read !== "undefined" && typeof readbuffer !== "undefined") {
    return new Promise((function(resolve, reject) {
      var rootURL = this.rootURL || pypyjs.rootURL;
      var data = read(rootURL + relpath);
      resolve({ responseText: data });
    }).bind(this));
  }
  return new Promise(function(resolve, reject) {
    reject("unable to fetch files");
  });
};

if (typeof localStorage !== "undefined") {
  var localStorage = false;
}

// pypyjs.prototype.fetch = function fetch(relpath, responseType) {
//   // For the web, use XMLHttpRequest.
//   var use_cache = pypyjs.cacheKey && localStorage;
//   if (use_cache) {
//     if (var item = localStorage.getItem(pypyjs.cacheKey+'-'+relpath)) {
//       resolve({ responseText: item });
//     }
//   }
//   if (typeof XMLHttpRequest !== "undefined") {
//     return new Promise((function(resolve, reject) {
//       var xhr = new XMLHttpRequest();
//       xhr.onload = function() {
//         if (xhr.status >= 400) {
//           reject(xhr)
//         } else {
//           console.log(xhr.responseText);
//           if (use_cache && xhr.responseText) {
//             localStorage.setItem(pypyjs.cacheKey+'-'+relpath, xhr.responseText);
//           }
//           resolve(xhr);
//         }
//       };
//       var rootURL = this.rootURL || pypyjs.rootURL;
//       xhr.open('GET', rootURL + relpath, true);
//       xhr.responseType = responseType || "text";
//       xhr.send(null);
//     }).bind(this));
//   }
//   // For nodejs, use fs.readFile.
//   if (typeof fs !== "undefined" && typeof fs.readFile !== "undefined") {
//     return new Promise((function(resolve, reject) {
//       var rootURL = this.rootURL || pypyjs.rootURL;
//       fs.readFile(path.join(rootURL, relpath), function(err, data) {
//         if (err) return reject(err);
//         resolve({ responseText: data.toString() });
//       });
//     }).bind(this));
//   }
//   // For spidermonkey, use snarf (which has a binary read mode).
//   if (typeof snarf !== "undefined") {
//     return new Promise((function(resolve, reject) {
//       var rootURL = this.rootURL || pypyjs.rootURL;
//       var data = snarf(rootURL + relpath);
//       resolve({ responseText: data });
//     }).bind(this));
//   }
//   // For d8, use read() and readbuffer().
//   if (typeof read !== "undefined" && typeof readbuffer !== "undefined") {
//     return new Promise((function(resolve, reject) {
//       var rootURL = this.rootURL || pypyjs.rootURL;
//       var data = read(rootURL + relpath);
//       resolve({ responseText: data });
//     }).bind(this));
//   }
//   return new Promise(function(resolve, reject) {
//     reject("unable to fetch files");
//   });
// };


// Method to execute python source directly in the VM.
//
// This is the basic way to push code into the pypyjs VM.
// Calling code should not use it directly; rather we use it
// as a primitive to build up a nicer execution API.
//
pypyjs.prototype._execute_source = function _execute_source(code) {
  var Module = this._module;
  code = "try:\n" +
         "  " + code + "\n" +
         "except Exception:\n" +
         "  typ, val, tb = sys.exc_info()\n" +
         "  err_name = getattr(typ, '__name__', str(typ))\n" +
         "  err_msg = str(val)\n" +
         "  err_trace = traceback.format_exception(typ, val, tb)\n" +
         "  err_trace = ''.join(err_trace)\n" +
         "  js.globals['pypyjs']._lastErrorName = err_name\n" +
         "  js.globals['pypyjs']._lastErrorMessage = err_msg\n" +
         "  js.globals['pypyjs']._lastErrorTrace = err_trace\n";
  var code_chars = Module.intArrayFromString(code);
  var code_ptr = Module.allocate(code_chars, 'i8', Module.ALLOC_NORMAL);
  if (!code_ptr) {
    return Promise.reject(new pypyjs.Error("Failed to allocate memory"));
  }
  var res = Module._pypy_execute_source(code_ptr);
  Module._free(code_ptr);
  // XXX TODO: races/re-entrancy on _lastError?
  if (pypyjs._lastErrorName) {
    var err = new pypyjs.Error(
      pypyjs._lastErrorName,
      pypyjs._lastErrorMessage,
      pypyjs._lastErrorTrace
    );
    pypyjs._lastErrorName = null;
    pypyjs._lastErrorMessage = null;
    pypyjs._lastErrorTrace = null;
    return Promise.reject(err);
  }
  if (res < 0) {
    return Promise.reject(new pypyjs.Error("Error executing python code"));
  }
  return Promise.resolve(null);
}


function _escape(value) {
  return value.replace(/\\/g, "\\\\").replace(/'/g, "\\'");
}


// Method to determine when the interpreter is ready.
//
// This method returns a promise that will resolve once the interpreter
// is ready for use.
//
pypyjs.prototype.ready = function ready() {
  return this._ready;
}


// Method to execute some python code.
//
// This passes the given python code to the VM for execution.
// It's fairly directly analogous to the "exec" statement in python.
// It is not possible to directly access the result of the code, if any.
// Rather you should store it into a variable and then use the get() method.
//
pypyjs.prototype.exec = function exec(code) {
  return this._ready.then((function() {
    var p = Promise.resolve();
    // Find any "import" statements in the code,
    // and ensure the modules are ready for loading.
    if (this.autoLoadModules) {
      p = p.then((function() {
        return this.findImportedNames(code);
      }).bind(this))
      .then((function(imports) {
        return this.loadModuleData.apply(this, imports);
      }).bind(this))
    }
    // Now we can execute the code in custom top-level scope.
    code = 'exec \'\'\'' + _escape(code) + '\'\'\' in top_level_scope';
    p = p.then((function() {
      return this._execute_source(code);
    }).bind(this));
    return p;
  }).bind(this));
}


// Method to evaluate an expression.
//
// This method evaluates an expression and returns its value (assuming the
// value can be translated into javascript).  It's fairly directly analogous
// to the "eval" function in python.
//
// For backwards-compatibility reasons, it will also evaluate statements.
// This behaviour is deprecated and will be removed in a future release.
//
pypyjs.prototype.eval = function (expr) {
  return this._ready.then((function() {
    // First try to execute it as an expression.
    code = "r = eval('" + _escape(expr) + "', top_level_scope)";
    return this._execute_source(code);
  }).bind(this)).then(
    (function() {
      // If that succeeded, return the result.
      return this.get("r", true)
    }).bind(this),
    (function(err) {
      if (err && err.name && err.name !== "SyntaxError") {
        throw err;
      }
      // If that failed, try again via exec().
      if (typeof console !== "undefined") {
        console.warn("Calling pypyjs.eval() with statements is deprecated.");
        console.warn("Use eval() for expressions, exec() for statements.");
      }
      return this.exec(expr);
    }).bind(this)
  )
}

// Method to evaluate some python code from a file..
//
// This fetches the named file and passes it to the VM for execution.
//
pypyjs.prototype.execfile = function execfile(filename) {
  return this.fetch(filename).then((function(xhr) {
    var code = xhr.responseText;
    return this.exec(code);
  }).bind(this));
}


// Method to read a python variable.
//
// This tries to convert the value in the named python variable into an
// equivalent javascript value and returns it.  It will fail if the variable
// does not exist or contains a value that cannot be converted.
//
pypyjs._resultsID = 0;
pypyjs._resultsMap = {};
pypyjs.prototype.get = function get(name, _fromGlobals) {
  var resid = ""+(pypyjs._resultsID++);
  // We can read from global scope for internal use; don't do this from calling code!
  if (_fromGlobals) {
    var namespace = "globals()";
  } else {
    var namespace = "top_level_scope";
  }
  return this._ready.then((function() {
    var code = namespace + ".get('" + _escape(name) + "', js.undefined)";
    code = "js.convert(" + code + ")"
    code = "js.globals['pypyjs']._resultsMap['" + resid + "'] = " + code;
    return this._execute_source(code);
  }).bind(this)).then((function() {
    var res = pypyjs._resultsMap[resid];
    delete pypyjs._resultsMap[resid];
    return res;
  }).bind(this));
}


// Method to set a python variable to a javascript value.
//
// This generates a handle to the given object, and arranges for the named
// python variable to reference it via that handle.
//
pypyjs.prototype.set = function set(name, value) {
  return this._ready.then((function() {
    var Module = this._module;
    var h = Module._emjs_make_handle(value);
    name = _escape(name);
    var code = "top_level_scope['" + name + "'] = js.Value(" + h + ")";
    return this._execute_source(code);
  }).bind(this));
}


// Method to run an interactive REPL.
//
// This method takes takes callback function implementing the user
// input prompt, and runs a REPL loop using it.  The prompt function
// may either return the input as a string, or a promise resolving to
// the input as a string.  If not specified, we read from stdin (which
// works fine in e.g. nodejs, but is almost certainly not what you want
// in the browser, because it's blocking).
//
pypyjs.prototype.repl = function repl(prmpt) {
  if (!prmpt) {
    // If there's a custom stdin, or we're not in nodejs, then we should
    // default to prompting on stdin/stdout.  For nodejs, we can build
    // an async prompt atop process.stdin.
    var buffer = "";
    if (this.stdin !== devNull.stdin || typeof process === "undefined") {
      prmpt = (function(ps1) {
        var input;
        this.stdout(ps1);
        var c = this.stdin();
        while (c) {
          var idx = c.indexOf("\n");
          if (idx >= 0) {
            var input = buffer + c.substr(0, idx + 1);
            buffer = c.substr(idx + 1);
            return input;
          }
          buffer += c;
          c = this.stdin();
        }
        input = buffer;
        buffer = "";
        return input;
      }).bind(this);
    } else {
      prmpt = (function(ps1) {
        return new Promise((function(resolve, reject) {
          this.stdout(ps1);
          var slurp = function() {
            process.stdin.once("readable", function() {
              var chunk = process.stdin.read();
              if (chunk === null) {
                slurp();
              } else {
                chunk = chunk.toString();
                var idx = chunk.indexOf("\n");
                if (idx < 0) {
                  buffer += chunk;
                  slurp();
                } else {
                  resolve(buffer + chunk.substr(0, idx + 1));
                  buffer = chunk.substr(idx + 1);
                }
              }
            });
          }
          slurp();
        }).bind(this));
      }).bind(this);
    }
  }
  // Set up an InteractiveConsole instance,
  // then loop forever via recursive promises.
  return this._ready.then((function() {
    return this.loadModuleData("code");
  }).bind(this)).then((function() {
    return this._execute_source("import code");
  }).bind(this)).then((function() {
    return this._execute_source("c = code.InteractiveConsole(top_level_scope)");
  }).bind(this)).then((function() {
    return this._repl_loop(prmpt, ">>> ");
  }).bind(this));
}


pypyjs.prototype._repl_loop = function _repl_loop(prmpt, ps1) {
  return Promise.resolve().then((function() {
    // Prompt for input, which may happen via async promise.
    return prmpt.call(this, ps1);
  }).bind(this)).then((function(input) {
    // Push it into the InteractiveConsole, a line at a time.
    var p = Promise.resolve();
    input.split("\n").forEach((function(line) {
      // Find any "import" statements in the code,
      // and ensure the modules are ready for loading.
      if (this.autoLoadModules) {
        p = p.then((function() {
          return this.findImportedNames(line);
        }).bind(this))
        .then((function(imports) {
          return this.loadModuleData.apply(this, imports);
        }).bind(this))
      }
      var code = 'r = c.push(\'' + _escape(line) + '\')';
      p = p.then((function() {
        return this._execute_source(code);
      }).bind(this));
    }).bind(this));
    return p;
  }).bind(this)).then((function() {
    // Check the result from the final push.
    return this.get("r", true)
  }).bind(this)).then((function(r) {
    // If r == 1, we're in a multi-line definition.
    // Adjust the prompt accordingly.
    if (r) {
      return this._repl_loop(prmpt, "... ");
    } else {
      return this._repl_loop(prmpt, ">>> ");
    }
  }).bind(this));
}


// Method to look for "import" statements in a code string.
// Returns a promise that will resolve to a list of imported module names.
//
// XXX TODO: this is far from complete and should not be done with a regex.
// Perhaps we can call into python's "ast" module for this parsing?
//
var importStatementRE = /(from\s+([a-zA-Z0-9_\.]+)\s+)?import\s+\(?\s*([a-zA-Z0-9_\.\*]+(\s+as\s+[a-zA-Z0-9_]+)?[ \t]*,?[ \t]*)+[ \t]*\)?/g
pypyjs.prototype.findImportedNames = function findImportedNames(code) {
  var match = null;
  var imports = [];
  importStatementRE.lastIndex = 0;
  while ((match = importStatementRE.exec(code)) !== null) {
    var relmod = match[2];
    if (relmod) {
      relmod = relmod + ".";
    } else {
      relmod = "";
    }
    var submods = match[0].split("import")[1];
    while (submods && /[\s(]/.test(submods.charAt(0))) {
      submods = submods.substr(1);
    }
    while (submods && /[\s)]/.test(submods.charAt(submods.length - 1))) {
      submods = submods.substr(0, submods.length - 1);
    }
    submods = submods.split(/\s*,\s*/);
    for (var i = 0; i < submods.length; i++) {
      var submod = submods[i];
      submod = submod.split(/\s*as\s*/)[0];
      imports.push(relmod + submod);
    }
  }
  return Promise.resolve(imports);
}


// Method to load the contents of a python module, along with
// any dependencies.  This populates the relevant paths within
// the VMs simulated filesystem so that is can find and import
// the specified module.
//
pypyjs.prototype.loadModuleData = function loadModuleData(/* names */) {
  // Each argument is a name that we want to import.
  // We must find the longest prefix that is an available module
  // and load it along with all its dependencies.
  var modules = Array.prototype.slice.call(arguments);
  return this._ready.then((function() {
    var toLoad = {};
    NEXTNAME: for (var i = 0; i < modules.length; i++) {
      var name = modules[i];
      // Find the nearest containing module for the given name.
      // Note that it may not match a module at all, in which case we ignore it.
      while (true) {
        if (this._allModules[name]) {
          break;
        }
        name = name.substr(0, name.lastIndexOf("."));
        if (!name) continue NEXTNAME;
      }
      this._findModuleDeps(name, toLoad);
    } 
    // Now ensure that each module gets loaded.
    // XXX TODO: we could load these concurrently.
    var p = Promise.resolve();
    for (var name in toLoad) {
      p = p.then(this._makeLoadModuleData(name));
    }
    return p;
  }).bind(this));
}


pypyjs.prototype._findModuleDeps = function _findModuleDeps(name, seen) {
  if (!seen) seen = {};
  var deps = [];
  // If we don't know about this module, ignore it.
  if (!this._allModules[name]) {
    return seen;
  }
  // Depend on any explicitly-named imports.
  var imports = this._allModules[name].imports;
  if (imports) {
    for (var i = 0; i < imports.length; i++) {
      deps.push(imports[i]);
    }
  }
  // Depend on the __init__.py for packages.
  if (this._allModules[name].dir) {
    deps.push(name + ".__init__");
  }
  // Include the parent package, if any.
  var idx = name.lastIndexOf(".");
  if (idx !== -1) {
    deps.push(name.substr(0, idx));
  }
  // Recurse for any previously-unseen dependencies.
  seen[name] = true;
  for (var i = 0; i < deps.length; i++) {
    if (!seen[deps[i]]) {
      this._findModuleDeps(deps[i], seen);
    }
  }
  return seen;
}


pypyjs.prototype._makeLoadModuleData = function _makeLoadModuleData(name) {
  return (function() {
    // If we've already loaded this module, we're done.
    if (this._loadedModules[name]) {
      return Promise.resolve();
    }
    // If we're already in the process of loading it, use the existing promise.
    if (this._pendingModules[name]) {
      return this._pendingModules[name];
    }
    // If it's a package directory, there's not actually anything to do.
    if (this._allModules[name].dir) {
      return Promise.resolve();
    }
    // We need to fetch the module file and write it out.
    var modfile = this._allModules[name].file;
    var p = this.fetch("modules/" + modfile)
    .then((function(xhr) {
      var contents = xhr.responseText;
      this._writeModuleFile(name, contents)
      delete this._pendingModules[name];
    }).bind(this))
    this._pendingModules[name] = p;
    return p;
  }).bind(this);
}


pypyjs.prototype._writeModuleFile = function _writeModuleFile(name, data) {
  var Module = this._module;
  var file = this._allModules[name].file;
  // Create the containing directory first.
  var dir = file.split("/").slice(0, -1).join("/")
  try {
    Module.FS_createPath("/lib/pypyjs/lib_pypy", dir, true, false);
  } catch (e) { }
  // Now we can safely create the file.
  var fullpath = "/lib/pypyjs/lib_pypy/" + file;
  Module.FS_createDataFile(fullpath, "", data, true, false, true);
  this._loadedModules[name] = true;
}


// An error class for reporting python exceptions back to calling code.
// XXX TODO: this could be a lot more user-friendly than a opaque error...

pypyjs.Error = function pypyjsError(name, message, trace) {
  if (name && typeof message === "undefined") {
    message = name;
    name = "";
  }
  this.name = name || "pypyjs.Error";
  this.message = message || "pypyjs Unknown Error";
  this.trace = trace || "";
}
pypyjs.Error.prototype = new Error();
pypyjs.Error.prototype.constructor = pypyjs.Error;



// XXX TODO: expose the filesystem for manipulation by calling code.


// Add convenience methods directly on the 'pypyjs' function, that
// will invoke corresponding methods on a default VM instance.
// This makes it look like 'pypyjs' is a singleton VM instance.

pypyjs._defaultVM = null;
pypyjs.stdin = stdio.stdin
pypyjs.stdout = stdio.stdout
pypyjs.stderr = stdio.stderr

var PUBLIC_NAMES = ['ready', 'exec', 'eval', 'execfile', 'get', 'set',
                    'repl', 'loadModuleData'];

PUBLIC_NAMES.forEach(function(name) {
  pypyjs[name] = function() {
    if (!pypyjs._defaultVM) {
      pypyjs._defaultVM = new pypyjs({
        stdin: function(){ return pypyjs.stdin.apply(this, arguments); },
        stdout: function(){ return pypyjs.stdout.apply(this, arguments); },
        stderr: function(){ return pypyjs.stderr.apply(this, arguments); },
      });
    }
    return pypyjs._defaultVM[name].apply(pypyjs._defaultVM, arguments)
  }
})


// For nodejs, run a repl when invoked directly from the command-line.

return pypyjs;

})();
