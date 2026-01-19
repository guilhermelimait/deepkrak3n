import type { AppType, DocumentType, NextComponentType } from '../shared/lib/utils';
import type { ClientReferenceManifest } from '../build/webpack/plugins/flight-manifest-plugin';
import type { PageConfig, GetStaticPaths, GetServerSideProps, GetStaticProps } from 'next/types';
import type { RouteModule } from './future/route-modules/route-module';
import { BuildManifest } from './get-page-files';
export type ManifestItem = {
    id: number | string;
    files: string[];
};
export type ReactLoadableManifest = {
    [moduleId: string]: ManifestItem;
};
export type LoadComponentsReturnType = {
    Component: NextComponentType;
    pageConfig: PageConfig;
    buildManifest: BuildManifest;
    subresourceIntegrityManifest?: Record<string, string>;
    reactLoadableManifest: ReactLoadableManifest;
    clientReferenceManifest?: ClientReferenceManifest;
    serverActionsManifest?: any;
    Document: DocumentType;
    App: AppType;
    getStaticProps?: GetStaticProps;
    getStaticPaths?: GetStaticPaths;
    getServerSideProps?: GetServerSideProps;
    ComponentMod: any;
    routeModule?: RouteModule;
    isAppPath?: boolean;
    page: string;
};
/**
 * Load manifest file with retries, defaults to 3 attempts.
 */
export declare function loadManifestWithRetries<T>(manifestPath: string, attempts?: number): Promise<T>;
declare function loadComponentsImpl({ distDir, page, isAppPath, }: {
    distDir: string;
    page: string;
    isAppPath: boolean;
}): Promise<LoadComponentsReturnType>;
export declare const loadComponents: typeof loadComponentsImpl;
export {};
