import { Kernel, ServiceManager } from '@jupyterlab/services';

function escapeForPython(s: string): string {
  return JSON.stringify(s);
}

function escapeForR(s: string): string {
  return JSON.stringify(s);
}

function escapeForJulia(s: string): string {
  return JSON.stringify(s);
}

function buildSnippet(
  language: string,
  key: string,
  value: string | null
): string | null {
  const lang = language.toLowerCase();

  if (lang === 'python') {
    if (value === null) {
      return `import os; os.environ.pop(${escapeForPython(key)}, None)`;
    }
    return `import os; os.environ[${escapeForPython(key)}] = ${escapeForPython(value)}`;
  }

  if (lang === 'r') {
    if (value === null) {
      return `Sys.unsetenv(${escapeForR(key)})`;
    }
    return `Sys.setenv(${escapeForR(key)} = ${escapeForR(value)})`;
  }

  if (lang === 'julia') {
    if (value === null) {
      return `delete!(ENV, ${escapeForJulia(key)})`;
    }
    return `ENV[${escapeForJulia(key)}] = ${escapeForJulia(value)}`;
  }

  return null;
}

async function getKernelLanguage(
  kernel: Kernel.IKernelConnection
): Promise<string> {
  try {
    const info = await kernel.info;
    return info.language_info.name;
  } catch {
    return 'unknown';
  }
}

export async function injectEnvVar(
  kernel: Kernel.IKernelConnection,
  key: string,
  value: string | null
): Promise<void> {
  const language = await getKernelLanguage(kernel);
  const code = buildSnippet(language, key, value);
  if (!code) {
    console.warn(
      `jupyterlab-env-sync: unsupported kernel language "${language}", skipping injection`
    );
    return;
  }

  const future = kernel.requestExecute({
    code,
    silent: true,
    store_history: false
  });
  await future.done;
}

export async function injectIntoAllKernels(
  serviceManager: ServiceManager.IManager,
  key: string,
  value: string | null
): Promise<void> {
  const kernelManager = serviceManager.kernels;
  const running = Array.from(kernelManager.running());

  await Promise.all(
    running.map(async model => {
      try {
        const kernel = kernelManager.connectTo({ model });
        await injectEnvVar(kernel, key, value);
      } catch (err) {
        console.error(
          `jupyterlab-env-sync: failed to inject into kernel ${model.id}:`,
          err
        );
      }
    })
  );
}

export { buildSnippet };
