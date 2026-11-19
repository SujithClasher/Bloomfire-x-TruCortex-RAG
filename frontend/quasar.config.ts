import { configure } from 'quasar/wrappers'

export default configure((/* ctx */) => ({
  boot: ['axios'],
  css: ['app.scss'],
  extras: ['material-icons', 'roboto-font'],
  build: {
    target: {
      browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1']
    },
    vueRouterMode: 'hash',
    typescript: { strict: true }
  },
  devServer: {
    port: 5173,
    open: true
  },
  framework: {
    config: { dark: false },
    plugins: ['Notify', 'Dialog', 'Loading']
  },
  animations: 'all'
}))
