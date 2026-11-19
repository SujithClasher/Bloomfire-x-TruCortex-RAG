import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Quasar, Notify, Dialog, Loading } from 'quasar'

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css'

// Import Quasar css (pre-compiled)
import 'quasar/dist/quasar.css'

// Import app css
import './css/app.css'

import App from './App.vue'

const app = createApp(App)

app.use(createPinia())
app.use(Quasar, {
  plugins: {
    Notify,
    Dialog,
    Loading
  },
  config: {
    notify: {
      position: 'top-right',
      timeout: 3500,
    }
  }
})

app.mount('#app')

