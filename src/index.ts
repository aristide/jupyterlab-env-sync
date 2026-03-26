import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IEnvSync } from './tokens';
import { EnvSync } from './env_sync';

const plugin: JupyterFrontEndPlugin<IEnvSync> = {
  id: 'jupyterlab-env-sync:plugin',
  autoStart: true,
  provides: IEnvSync,
  activate: (app: JupyterFrontEnd): IEnvSync => {
    console.log('jupyterlab-env-sync: extension activated');
    return new EnvSync(app);
  }
};

export default plugin;
export { IEnvSync } from './tokens';
export type { IEnvEntry } from './tokens';
