package com.cryptosignals.app

import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import com.google.firebase.messaging.FirebaseMessaging
import java.util.Locale

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var adapter: SignalAdapter
    private lateinit var swipeRefresh: SwipeRefreshLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Request Notification Permission for Android 13+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 101)
            }
        }

        // Subscribe to notifications based on language
        val lang = Locale.getDefault().language
        val topic = if (lang == "ar") "signals_ar" else "signals_en"
        
        FirebaseMessaging.getInstance().subscribeToTopic(topic)
            .addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    Log.d("FCM", "Subscribed to $topic")
                } else {
                    Log.w("FCM", "Subscribe failed", task.exception)
                }
            }

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        swipeRefresh = findViewById(R.id.swipeRefresh)
        
        recyclerView.layoutManager = LinearLayoutManager(this)
        adapter = SignalAdapter(emptyList())
        recyclerView.adapter = adapter

        swipeRefresh.setOnRefreshListener {
            fetchSignals()
        }

        // Initial fetch
        fetchSignals()

        // Check for notification intent extras
        intent?.extras?.let {
            val title = it.getString("notification_title")
            val body = it.getString("notification_body")
            if (title != null && body != null) {
                showNotificationDialog(title, body)
            }
        }
    }

    override fun onNewIntent(intent: android.content.Intent?) {
        super.onNewIntent(intent)
        intent?.extras?.let {
            val title = it.getString("notification_title")
            val body = it.getString("notification_body")
            if (title != null && body != null) {
                showNotificationDialog(title, body)
            }
        }
    }

    private fun fetchSignals() {
        swipeRefresh.isRefreshing = true
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = RetrofitClient.instance.getSignals()
                withContext(Dispatchers.Main) {
                    adapter.updateData(response.data)
                    swipeRefresh.isRefreshing = false
                }
            } catch (e: Exception) {
                Log.e("CryptoSignals", "Error fetching signals", e)
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_LONG).show()
                    swipeRefresh.isRefreshing = false
                }
            }
        }
    }

    private fun showNotificationDialog(title: String, body: String) {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(body)
            .setPositiveButton("OK") { dialog, _ -> dialog.dismiss() }
            .show()
    }

    private fun showHistoryDialog() {
        val prefs = getSharedPreferences("crypto_prefs", android.content.Context.MODE_PRIVATE)
        val historySet = prefs.getStringSet("notification_history", emptySet()) ?: emptySet()
        
        val list = historySet.toList().sortedByDescending { it.split("|")[0].toLong() }
        val displayList = list.map { 
            val parts = it.split("|")
            if (parts.size >= 3) "${parts[1]}\n${parts[2]}" else it 
        }.toTypedArray()

        if (displayList.isEmpty()) {
            Toast.makeText(this, "No notifications yet", Toast.LENGTH_SHORT).show()
            return
        }

        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Notifications")
            .setItems(displayList, null)
            .setPositiveButton("Close") { dialog, _ -> dialog.dismiss() }
            .show()
    }
}
