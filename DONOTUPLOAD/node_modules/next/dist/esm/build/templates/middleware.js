import "../../server/web/globals";
import { adapter } from "../../server/web/adapter";
// Import the userland code.
// @ts-expect-error - replaced by webpack/turbopack loader
import * as _mod from "VAR_USERLAND";
const mod = {
    ..._mod
};
const handler = mod.middleware || mod.default;
if (typeof handler !== "function") {
    throw new Error(`The Middleware must export a \`middleware\` or a \`default\` function`);
}
export default function(opts) {
    return adapter({
        ...opts,
        page: "",
        handler
    });
}

//# sourceMappingURL=middleware.js.map