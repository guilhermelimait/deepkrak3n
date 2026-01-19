/// <reference types="node" />
/// <reference types="node" />
import type { FindComponentsResult } from '../next-server';
import type { LoadComponentsReturnType } from '../load-components';
import type { Options as ServerOptions } from '../next-server';
import type { Params } from '../../shared/lib/router/utils/route-matcher';
import type { ParsedUrl } from '../../shared/lib/router/utils/parse-url';
import type { ParsedUrlQuery } from 'querystring';
import type { UrlWithParsedQuery } from 'url';
import type { BaseNextRequest, BaseNextResponse } from '../base-http';
import type { MiddlewareRoutingItem } from '../base-server';
import type { RouteMatch } from '../future/route-matches/route-match';
import type { RouteMatcherManager } from '../future/route-matcher-managers/route-matcher-manager';
import type { NextParsedUrlQuery, NextUrlWithParsedQuery } from '../request-meta';
import Server from '../next-server';
import { NodeNextResponse, NodeNextRequest } from '../base-http/node';
import { PagesManifest } from '../../build/webpack/plugins/pages-manifest-plugin';
import { IncrementalCache } from '../lib/incremental-cache';
export interface Options extends ServerOptions {
    /**
     * Tells of Next.js is running from the `next dev` command
     */
    isNextDevCommand?: boolean;
}
export default class DevServer extends Server {
    private devReady;
    private setDevReady?;
    protected sortedRoutes?: string[];
    private pagesDir?;
    private appDir?;
    private actualMiddlewareFile?;
    private actualInstrumentationHookFile?;
    private middleware?;
    private originalFetch;
    private staticPathsCache;
    private invokeDevMethod;
    protected staticPathsWorker?: {
        [key: string]: any;
    } & {
        loadStaticPaths: typeof import('./static-paths-worker').loadStaticPaths;
    };
    private getStaticPathsWorker;
    constructor(options: Options);
    protected getRouteMatchers(): RouteMatcherManager;
    protected getBuildId(): string;
    protected prepareImpl(): Promise<void>;
    protected close(): Promise<void>;
    protected hasPage(pathname: string): Promise<boolean>;
    runMiddleware(params: {
        request: BaseNextRequest;
        response: BaseNextResponse;
        parsedUrl: ParsedUrl;
        parsed: UrlWithParsedQuery;
        middlewareList: MiddlewareRoutingItem[];
    }): Promise<import("../web/types").FetchEventResult | {
        finished: boolean;
    }>;
    runEdgeFunction(params: {
        req: BaseNextRequest;
        res: BaseNextResponse;
        query: ParsedUrlQuery;
        params: Params | undefined;
        page: string;
        appPaths: string[] | null;
        isAppPath: boolean;
    }): Promise<import("../web/types").FetchEventResult | null>;
    handleRequest(req: BaseNextRequest, res: BaseNextResponse, parsedUrl?: NextUrlWithParsedQuery): Promise<void>;
    run(req: NodeNextRequest, res: NodeNextResponse, parsedUrl: UrlWithParsedQuery): Promise<void>;
    protected logErrorWithOriginalStack(err?: unknown, type?: 'unhandledRejection' | 'uncaughtException' | 'warning' | 'app-dir'): Promise<void>;
    protected getPagesManifest(): PagesManifest | undefined;
    protected getAppPathsManifest(): PagesManifest | undefined;
    protected getMiddleware(): MiddlewareRoutingItem | undefined;
    protected getNextFontManifest(): undefined;
    protected hasMiddleware(): Promise<boolean>;
    protected ensureMiddleware(): Promise<void>;
    private runInstrumentationHookIfAvailable;
    protected ensureEdgeFunction({ page, appPaths, }: {
        page: string;
        appPaths: string[] | null;
    }): Promise<void>;
    generateRoutes(_dev?: boolean): void;
    _filterAmpDevelopmentScript(html: string, event: {
        line: number;
        col: number;
        code: string;
    }): boolean;
    protected getStaticPaths({ pathname, requestHeaders, page, isAppPath, }: {
        pathname: string;
        requestHeaders: IncrementalCache['requestHeaders'];
        page: string;
        isAppPath: boolean;
    }): Promise<{
        staticPaths?: string[];
        fallbackMode?: false | 'static' | 'blocking';
    }>;
    private restorePatchedGlobals;
    protected ensurePage(opts: {
        page: string;
        clientOnly: boolean;
        appPaths?: ReadonlyArray<string> | null;
        match?: RouteMatch;
    }): Promise<void>;
    protected findPageComponents({ page, query, params, isAppPath, appPaths, shouldEnsure, }: {
        page: string;
        query: NextParsedUrlQuery;
        params: Params;
        isAppPath: boolean;
        sriEnabled?: boolean;
        appPaths?: ReadonlyArray<string> | null;
        shouldEnsure: boolean;
    }): Promise<FindComponentsResult | null>;
    protected getFallbackErrorComponents(): Promise<LoadComponentsReturnType | null>;
    getCompilationError(page: string): Promise<any>;
}
