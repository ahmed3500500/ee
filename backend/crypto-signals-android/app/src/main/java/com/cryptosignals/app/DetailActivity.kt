package com.cryptosignals.app

import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class DetailActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_detail)

        val pair = intent.getStringExtra("pair") ?: "BTC/USDT"
        // Convert pair format from "BTC/USDT" to "BTCUSDT" for TradingView
        val symbol = pair.replace("/", "")

        val webView = findViewById<WebView>(R.id.webView)
        webView.settings.javaScriptEnabled = true
        webView.webViewClient = WebViewClient()

        val html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>body { margin: 0; padding: 0; background-color: #ffffff; }</style>
            </head>
            <body>
                <div class="tradingview-widget-container">
                    <div id="tradingview_chart"></div>
                    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                    <script type="text/javascript">
                    new TradingView.widget(
                    {
                        "width": "100%",
                        "height": "100%",
                        "symbol": "BINANCE:$symbol",
                        "interval": "60",
                        "timezone": "Etc/UTC",
                        "theme": "light",
                        "style": "1",
                        "locale": "en",
                        "toolbar_bg": "#f1f3f6",
                        "enable_publishing": false,
                        "allow_symbol_change": true,
                        "container_id": "tradingview_chart"
                    }
                    );
                    </script>
                </div>
                <style>
                    html, body, .tradingview-widget-container { height: 100%; width: 100%; }
                </style>
            </body>
            </html>
        """.trimIndent()

        webView.loadData(html, "text/html", "UTF-8")
    }
}