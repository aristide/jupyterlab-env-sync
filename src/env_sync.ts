import { ServiceManager, ServerConnection } from '@jupyterlab/services';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { URLExt } from '@jupyterlab/coreutils';
import { IEnvSync, IEnvEntry } from './tokens';
import { injectIntoAllKernels } from './kernel_inject';
import { restartTerminals } from './terminal_restart';

const API_NAMESPACE = 'jupyterlab-env-sync/env';

export class EnvSync implements IEnvSync {
  private _serviceManager: ServiceManager.IManager;
  private _serverSettings: ServerConnection.ISettings;

  constructor(app: JupyterFrontEnd) {
    this._serviceManager = app.serviceManager;
    this._serverSettings = app.serviceManager.serverSettings;
  }

  private _url(path?: string): string {
    const parts = path ? `${API_NAMESPACE}/${path}` : API_NAMESPACE;
    return URLExt.join(this._serverSettings.baseUrl, parts);
  }

  private async _request(
    url: string,
    method: string,
    body?: any
  ): Promise<any> {
    const init: RequestInit = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    if (body !== undefined) {
      init.body = JSON.stringify(body);
    }
    const response = await ServerConnection.makeRequest(
      url,
      init,
      this._serverSettings
    );
    if (!response.ok) {
      const text = await response.text();
      throw new ServerConnection.ResponseError(response, text);
    }
    return response.json();
  }

  async setVar(extensionId: string, key: string, value: string): Promise<void> {
    await this._request(this._url(encodeURIComponent(key)), 'PUT', {
      extension_id: extensionId,
      value
    });
    await this._propagate(key, value);
  }

  async resetVar(
    extensionId: string,
    key: string,
    force?: boolean
  ): Promise<void> {
    await this._request(this._url(encodeURIComponent(key)), 'DELETE', {
      extension_id: extensionId,
      force: force ?? false
    });
    await this._propagate(key, null);
  }

  async getAll(): Promise<Record<string, IEnvEntry>> {
    return this._request(this._url(), 'GET');
  }

  async getByExtension(extensionId: string): Promise<Record<string, string>> {
    const url =
      this._url() + `?extension_id=${encodeURIComponent(extensionId)}`;
    return this._request(url, 'GET');
  }

  async resetAllByExtension(extensionId: string): Promise<void> {
    const data = await this._request(
      this._url(`extension/${encodeURIComponent(extensionId)}`),
      'DELETE'
    );
    const keys: string[] = data.reset_keys || [];
    await Promise.all(
      keys.map(k => injectIntoAllKernels(this._serviceManager, k, null))
    );
    if (keys.length > 0) {
      await restartTerminals(this._serviceManager);
    }
  }

  private async _propagate(key: string, value: string | null): Promise<void> {
    await injectIntoAllKernels(this._serviceManager, key, value);
    await restartTerminals(this._serviceManager);
  }
}
