export declare function createSelfSignedCertificate(host?: string, certDir?: string): Promise<{
    key: string;
    cert: string;
} | undefined>;
