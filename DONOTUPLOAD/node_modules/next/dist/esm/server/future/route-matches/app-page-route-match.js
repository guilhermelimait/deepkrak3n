import { RouteKind } from "../route-kind";
/**
 * Checks if the given match is an App Page route match.
 * @param match the match to check
 * @returns true if the match is an App Page route match, false otherwise
 */ export function isAppPageRouteMatch(match) {
    return match.definition.kind === RouteKind.APP_PAGE;
}

//# sourceMappingURL=app-page-route-match.js.map