/// <reference types="node" />
import type { NextConfigComplete } from '../../config-shared';
import { Telemetry } from '../../../telemetry/storage';
import { IncomingMessage, ServerResponse } from 'http';
import { UnwrapPromise } from '../../../lib/coalesced-function';
import { MiddlewareMatcher } from '../../../build/analysis/get-page-static-info';
import { MiddlewareRouteMatch } from '../../../shared/lib/router/utils/middleware-route-matcher';
import type { RenderWorkers } from '../router-server';
import { NextJsHotReloaderInterface } from '../../dev/hot-reloader-types';
type SetupOpts = {
    renderWorkers: RenderWorkers;
    dir: string;
    turbo?: boolean;
    appDir?: string;
    pagesDir?: string;
    telemetry: Telemetry;
    isCustomServer?: boolean;
    fsChecker: UnwrapPromise<ReturnType<typeof import('./filesystem').setupFsCheck>>;
    nextConfig: NextConfigComplete;
    port: number;
};
export declare function setupDev(opts: SetupOpts): Promise<{
    serverFields: {
        actualMiddlewareFile?: string | undefined;
        actualInstrumentationHookFile?: string | undefined;
        appPathRoutes?: Record<string, string | string[]> | undefined;
        middleware?: {
            page: string;
            match: MiddlewareRouteMatch;
            matchers?: MiddlewareMatcher[] | undefined;
        } | undefined;
        hasAppNotFound?: boolean | undefined;
        interceptionRoutes?: {
            match: import("../../../shared/lib/router/utils/path-match").PatchMatcher;
            check?: boolean | undefined;
        }[] | undefined;
    };
    hotReloader: NextJsHotReloaderInterface;
    requestHandler: (req: IncomingMessage, res: ServerResponse<IncomingMessage>) => Promise<{
        finished: boolean;
    }>;
    logErrorWithOriginalStack: (err: unknown, type?: "warning" | "uncaughtException" | "unhandledRejection" | "app-dir" | undefined) => Promise<void>;
    ensureMiddleware(): Promise<void>;
}>;
export {};
