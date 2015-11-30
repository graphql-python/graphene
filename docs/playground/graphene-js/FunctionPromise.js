//
// FunctionPromise: possibly-asynchronous function constructor.
//
// This is a prototype polyfill for a FunctionPromise object as described in:
//
//    https://bugzilla.mozilla.org/show_bug.cgi?id=854627
//
// Where possible it will arrange for the function body to be parsed/compiled
// off of the main thread, with the function object returned asynchronously
// via a promise.  The fallback implementation processes just falls back to
// the standard synchronous Function() constructor.
// 
// It doesn't (yet) have the following features from the linked proposal:
//
//    * ability to copy to different workers
//    * ability to store in IndexedDB
// 
function FunctionPromise(/* [args1[, args2[, ...argN]],], functionBody) */) {

  var useFallback =
    typeof window === "undefined" ||
    window.FunctionPromise !== FunctionPromise ||
    typeof document === "undefined" ||
    typeof document.createElement === "undefined" ||
    typeof document.head === "undefined" ||
    typeof document.head.appendChild === "undefined" ||
    typeof Blob === "undefined" ||
    typeof URL === "undefined" ||
    typeof URL.createObjectURL === "undefined";

  var args = Array.prototype.slice.call(arguments);

  // For the fallback case, we just use the normal Function constructor.

  if (useFallback) {
    try {
      var fn = Function.apply(null, args);
      return Promise.resolve(fn);
    } catch (err) {
      return Promise.reject(err);
    }
  }

  // If we have all the necessary pieces, we can do this asynchronously
  // by writing a <script> tag into the DOM.

  var funcid = FunctionPromise._nextid++;

  return new Promise(function(resolve, reject) {
    try {
      var funcSrc = [];
      funcSrc.push("window.FunctionPromise._results[" + funcid + "]=");
      funcSrc.push("function(");
      if (args.length > 1) {
        funcSrc.push(args[0]);
        for (var i = 1; i < args.length - 1; i++) {
          funcSrc.push(",");
          funcSrc.push(args[i]);
        }
      }
      funcSrc.push("){");
      funcSrc.push(args[args.length - 1]);
      funcSrc.push("}");
      var dataUrl = URL.createObjectURL(new Blob(funcSrc));
      var scriptTag = document.createElement("script");
      var cleanup = function() {
        URL.revokeObjectURL(dataUrl);
        scriptTag.remove();
        delete window.FunctionPromise._results[funcid];
      }
      scriptTag.onerror = function() {
        reject(new Error("unknown error loading FunctionPromise"))
        cleanup();
      }
      scriptTag.onload = function() {
        if (window.FunctionPromise._results[funcid]) {
          resolve(window.FunctionPromise._results[funcid]);
        } else {
          // No function, something must have gone wrong.
          // Likely a syntax error in the function body string.
          // Fall back to Function() constructor to surface it.
          try {
            Function.apply(null, args);
            reject(new Error("unknown error fulfilling FunctionPromise"));
          } catch (err) {
            reject(err);
          }
        }
        cleanup();
      }
      scriptTag.src = dataUrl;
      document.head.appendChild(scriptTag);
    } catch (err) {
      reject(err);
    }
  });
}

FunctionPromise._nextid = 0;
FunctionPromise._results = {};

if (typeof module !== "undefined" && typeof module.exports !== "undefined") {
  if (typeof Promise === "undefined") {
    Promise = require('es6-promise').Promise;
  }
  module.exports = FunctionPromise;
}
