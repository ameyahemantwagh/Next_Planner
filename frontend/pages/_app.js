import '../styles/globals.css'
import AppProviders from '../providers/AppProviders'
import AppShell from '../components/layout/AppShell'

export default function MyApp({ Component, pageProps }) {
  return (
    <AppProviders>
      <AppShell>
        <Component {...pageProps} />
      </AppShell>
    </AppProviders>
  )
}
