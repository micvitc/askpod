import Head from 'next/head';
import "../styles/global.css";

function MyApp({ Component, pageProps }) {
  return (
    <>
      <Head>
        <title>AskPod</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}

export default MyApp;