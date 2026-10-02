(function (global) {
  function levenshtein(a, b) {
    var matrix = [];
    var i, j;
    for (i = 0; i <= b.length; i++) {
      matrix[i] = [i];
    }
    for (j = 0; j <= a.length; j++) {
      matrix[0][j] = j;
    }
    for (i = 1; i <= b.length; i++) {
      for (j = 1; j <= a.length; j++) {
        if (b.charAt(i - 1) === a.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    return matrix[b.length][a.length];
  }

  function AICompareApi(dataSource) {
    this.models = [];
    this.byId = {};
    this.byName = {};
    this.allKeys = [];

    if (dataSource) {
      this.setData(dataSource);
    }
  }

  AICompareApi.prototype.setData = function (data) {
    this.models = Array.isArray(data) ? data : [];
    this.byId = {};
    this.byName = {};
    this.allKeys = [];

    for (var i = 0; i < this.models.length; i++) {
      var m = this.models[i];
      var mid = (m.model_id || "").toString().trim().toLowerCase();
      var name = (m.name || "").toString().trim().toLowerCase();

      if (mid) {
        this.byId[mid] = m;
        if (this.allKeys.indexOf(mid) === -1) {
          this.allKeys.push(mid);
        }
      }
      if (name) {
        this.byName[name] = m;
        if (this.allKeys.indexOf(name) === -1) {
          this.allKeys.push(name);
        }
      }
    }
  };

  AICompareApi.prototype.loadData = function (url) {
    var self = this;
    var targetUrl = url || "data/all.json";
    return fetch(targetUrl)
      .then(function (res) {
        if (!res.ok) {
          throw new Error("failed to fetch models data: " + res.status);
        }
        return res.json();
      })
      .then(function (data) {
        self.setData(data);
        return data;
      });
  };

  AICompareApi.prototype.normalize = function (str) {
    if (!str) return "";
    return str.toString().trim().toLowerCase();
  };

  AICompareApi.prototype.findClosest = function (query) {
    var clean = this.normalize(query);
    if (!clean) return { bestMatch: null, suggestions: [] };

    if (this.byId[clean]) {
      return { bestMatch: this.byId[clean].model_id, suggestions: [this.byId[clean].model_id] };
    }
    if (this.byName[clean]) {
      return { bestMatch: this.byName[clean].model_id, suggestions: [this.byName[clean].model_id] };
    }

    var scored = [];
    var seen = {};

    for (var i = 0; i < this.allKeys.length; i++) {
      var key = this.allKeys[i];
      var model = this.byId[key] || this.byName[key];
      if (!model || seen[model.model_id]) continue;

      var dist = levenshtein(clean, key);
      var bonus = 0;
      if (key.indexOf(clean) !== -1 || clean.indexOf(key) !== -1) {
        bonus = -4;
      }
      var finalScore = dist + bonus;

      scored.push({ modelId: model.model_id, score: finalScore });
      seen[model.model_id] = true;
    }

    scored.sort(function (a, b) {
      return a.score - b.score;
    });

    var topSuggestions = scored.slice(0, 5).map(function (item) {
      return item.modelId;
    });

    return {
      bestMatch: topSuggestions[0] || null,
      suggestions: topSuggestions
    };
  };

  AICompareApi.prototype.getModel = function (name, options) {
    var opts = options || {};
    var clean = this.normalize(name);

    if (this.byId[clean]) {
      return { status: "success", data: this.byId[clean] };
    }
    if (this.byName[clean]) {
      return { status: "success", data: this.byName[clean] };
    }

    var match = this.findClosest(clean);

    if (opts.autoFuzzy && match.bestMatch) {
      return {
        status: "success",
        auto_matched: true,
        searched: name,
        matched_model_id: match.bestMatch,
        data: this.byId[match.bestMatch]
      };
    }

    return {
      status: "error",
      message: "model '" + name + "' not found",
      searched: name,
      suggestion: match.bestMatch,
      all_suggestions: match.suggestions,
      hint: "set autoFuzzy to true to automatically select closest model"
    };
  };

  AICompareApi.prototype.compare = function (modelNames, options) {
    var opts = options || {};
    if (!Array.isArray(modelNames) || modelNames.length < 2) {
      return {
        status: "error",
        message: "please provide at least 2 models to compare"
      };
    }

    var resolved = [];
    var errors = [];
    var seenIds = {};

    for (var i = 0; i < modelNames.length; i++) {
      var raw = modelNames[i];
      var res = this.getModel(raw, opts);
      if (res.status === "success") {
        var m = res.data;
        if (!seenIds[m.model_id]) {
          seenIds[m.model_id] = true;
          var copy = Object.assign({}, m);
          if (res.auto_matched) {
            copy.auto_matched_from = raw;
          }
          resolved.push(copy);
        }
      } else {
        errors.push(res);
      }
    }

    if (errors.length > 0 && !opts.autoFuzzy) {
      return {
        status: "error",
        message: "some models could not be found",
        unresolved: errors
      };
    }

    if (resolved.length < 2) {
      return {
        status: "error",
        message: "at least 2 valid models are required after resolution",
        resolved: resolved,
        errors: errors
      };
    }

    resolved.sort(function (a, b) {
      var valA = a.conservative !== null && a.conservative !== undefined ? a.conservative : -999999;
      var valB = b.conservative !== null && b.conservative !== undefined ? b.conservative : -999999;
      return valB - valA;
    });

    var winner = resolved[0];

    return {
      status: "success",
      total_compared: resolved.length,
      winner: {
        model_id: winner.model_id,
        name: winner.name,
        conservative: winner.conservative,
        rank: winner.rank
      },
      models: resolved
    };
  };

  AICompareApi.prototype.getProperty = function (name, propertyName, options) {
    var opts = options || {};
    var modelRes = this.getModel(name, opts);
    if (modelRes.status !== "success") {
      return modelRes;
    }

    var model = modelRes.data;
    var cleanProp = this.normalize(propertyName).replace(/-/g, "_").replace(/\s+/g, "_");

    var foundKey = null;
    var keys = Object.keys(model);
    for (var i = 0; i < keys.length; i++) {
      if (keys[i].toLowerCase() === cleanProp) {
        foundKey = keys[i];
        break;
      }
    }

    if (!foundKey) {
      return {
        status: "error",
        message: "property '" + propertyName + "' not found on model '" + model.name + "'",
        available_properties: keys
      };
    }

    return {
      status: "success",
      model_id: model.model_id,
      model_name: model.name,
      property: foundKey,
      value: model[foundKey]
    };
  };

  AICompareApi.prototype.getLeaderboard = function (limit) {
    var ranked = this.models.filter(function (m) {
      return m.conservative !== null && m.conservative !== undefined;
    });

    ranked.sort(function (a, b) {
      return b.conservative - a.conservative;
    });

    var count = limit ? parseInt(limit, 10) : ranked.length;
    var slice = ranked.slice(0, count);

    return {
      status: "success",
      count: slice.length,
      leaderboard: slice
    };
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = AICompareApi;
  } else {
    global.AICompareApi = AICompareApi;
  }
})(typeof window !== "undefined" ? window : globalThis);
