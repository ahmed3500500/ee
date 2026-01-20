package com.cryptosignals.app

import retrofit2.http.GET

interface CryptoApi {
    @GET("android/signals")
    suspend fun getSignals(): SignalResponse
}
