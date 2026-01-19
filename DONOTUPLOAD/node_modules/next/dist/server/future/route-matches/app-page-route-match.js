"use strict";
Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, "isAppPageRouteMatch", {
    enumerable: true,
    get: function() {
        return isAppPageRouteMatch;
    }
});
const _routekind = require("../route-kind");
function isAppPageRouteMatch(match) {
    return match.definition.kind === _routekind.RouteKind.APP_PAGE;
}

//# sourceMappingURL=app-page-route-match.js.map