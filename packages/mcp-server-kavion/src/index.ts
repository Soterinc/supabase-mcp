import packageJson from '../package.json' with { type: 'json' };

export { 
  createKavionMcpServer, 
  type KavionMcpServerOptions 
} from './server.js';

export const version = packageJson.version;