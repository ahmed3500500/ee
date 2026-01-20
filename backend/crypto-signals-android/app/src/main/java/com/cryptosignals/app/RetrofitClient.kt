package com.cryptosignals.app

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
    // 10.0.2.2 is localhost for Android Emulator, but for APK we need real IP
    // Your PC IP: 208.110.70.114
    private const val BASE_URL = "http://208.110.70.114:8000/"

    val instance: CryptoApi by lazy {
        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        retrofit.create(CryptoApi::class.java)
    }
}
