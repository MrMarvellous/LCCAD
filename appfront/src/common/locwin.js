(function(global, undefined) {
  if (global.LOCWIN) {
    return;
  }

  var LOCWIN = global.LOCWIN = {
    version: '1.0.0',
  };

  LOCWIN.userInfo = {
    get: function() {
      return LOCWIN.Cache.get('userInfo');
    },
    set: function(userInfo) {
      return LOCWIN.Cache.set('userInfo', userInfo);
    },
    remove: function() {
      LOCWIN.Cache.remove('userInfo');
    }
  }

  LOCWIN.Cache = {
    get: function(key) {
      if (typeof key != 'string') return;

      var value = null;
      var str = global.sessionStorage.getItem(key);
      try {
        value = JSON.parse(str);
      } catch (e) {
        value = str;
      }

      return value;
    },
    set: function(key, value) {
      if (typeof key != 'string') return;
      if (typeof value == 'object') {
        value = JSON.stringify(value);
      }
      try {
        global.sessionStorage.setItem(key, value);
      } catch (e) {
        console.log(e);
      }
    },
    remove: function(key) {
      if (typeof key != 'string') return;
      global.sessionStorage.removeItem(key);
    },
    clear: function() {
      global.sessionStorage.clear();
    }
  };
  LOCWIN.loading = function(title, msg) {}

  LOCWIN.loaded = function() {}

})(window);
