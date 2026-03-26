import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

/**
 * Initialization data for the jupyterlab-env-sync extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-env-sync:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension jupyterlab-env-sync is activated!');
  }
};

export default plugin;
