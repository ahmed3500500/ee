package com.cryptosignals.app

data class SignalResponse(
    val status: String,
    val data: List<Signal>
)

data class Signal(
    val id: String,
    val coin: String,
    val pair: String,
    val price: String,
    val image_url: String,
    val score_value: Int,
    val score_color: String,
    val status_text: String,
    val entry: String,
    val targets: String,
    val stop_loss: String,
    val time_ago: String
)
