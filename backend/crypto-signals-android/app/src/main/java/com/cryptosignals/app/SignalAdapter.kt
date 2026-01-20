package com.cryptosignals.app

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class SignalAdapter(private var signals: List<Signal>) : RecyclerView.Adapter<SignalAdapter.SignalViewHolder>() {

    class SignalViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val coinName: TextView = view.findViewById(R.id.textCoin)
        val price: TextView = view.findViewById(R.id.textPrice)
        val score: TextView = view.findViewById(R.id.textScore)
        val status: TextView = view.findViewById(R.id.textStatus)
        val targets: TextView = view.findViewById(R.id.textTargets)
        val stopLoss: TextView = view.findViewById(R.id.textStopLoss)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): SignalViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_signal, parent, false)
        return SignalViewHolder(view)
    }

    override fun onBindViewHolder(holder: SignalViewHolder, position: Int) {
        val signal = signals[position]
        holder.coinName.text = signal.pair
        holder.price.text = signal.price
        holder.score.text = "${signal.score_value}"
        holder.status.text = signal.status_text
        holder.targets.text = signal.targets
        holder.stopLoss.text = signal.stop_loss
        
        try {
            holder.score.setTextColor(Color.parseColor(signal.score_color))
        } catch (e: Exception) {
            holder.score.setTextColor(Color.GREEN)
        }
    }

    override fun getItemCount() = signals.size

    fun updateData(newSignals: List<Signal>) {
        signals = newSignals
        notifyDataSetChanged()
    }
}
