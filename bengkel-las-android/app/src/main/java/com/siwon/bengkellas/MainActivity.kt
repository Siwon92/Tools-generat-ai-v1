package com.siwon.bengkellas

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

data class Order(val customer: String, val job: String, val total: Long)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); setContent { BengkelLasApp() } }
}

@Composable fun BengkelLasApp() {
    var tab by remember { mutableIntStateOf(0) }
    var orders by remember { mutableStateOf(listOf<Order>()) }
    Scaffold(bottomBar = { NavigationBar { listOf("Dashboard","Pesanan","Kalkulator").forEachIndexed { i, s -> NavigationBarItem(selected=tab==i,onClick={tab=i},icon={},label={Text(s)}) } } }) { p ->
        when(tab) { 0 -> Dashboard(Modifier.padding(p), orders); 1 -> Orders(Modifier.padding(p), orders) { orders = orders + it }; else -> Calculator(Modifier.padding(p)) }
    }
}

@Composable fun Dashboard(m: Modifier, orders: List<Order>) { LazyColumn(m.padding(18.dp)) { item { Text("KARYA TUNAS MUDA", style=MaterialTheme.typography.headlineSmall); Text("Manajemen Bengkel Las"); Spacer(Modifier.height(20.dp)); Card { Column(Modifier.padding(18.dp)) { Text("Total pesanan: ${orders.size}"); Text("Omzet tercatat: Rp ${orders.sumOf{it.total}}") } }; Spacer(Modifier.height(16.dp)); Text("Fitur utama",style=MaterialTheme.typography.titleMedium); Text("Pesanan pelanggan\nKalkulator bahan dan harga\nCatatan biaya & keuntungan\nEstimasi pagar, kanopi, railing, meja, kursi, dan lainnya") } } }

@Composable fun Orders(m: Modifier, orders: List<Order>, add: (Order)->Unit) { var customer by remember{mutableStateOf("")}; var job by remember{mutableStateOf("")}; var total by remember{mutableStateOf("")}; LazyColumn(m.padding(18.dp)) { item { Text("Pesanan Bengkel",style=MaterialTheme.typography.headlineSmall); OutlinedTextField(customer,{customer=it},label={Text("Nama pelanggan")},modifier=Modifier.fillMaxWidth()); OutlinedTextField(job,{job=it},label={Text("Jenis pekerjaan")},modifier=Modifier.fillMaxWidth()); OutlinedTextField(total,{total=it.filter(Char::isDigit)},label={Text("Nilai pekerjaan (Rp)")},modifier=Modifier.fillMaxWidth()); Button(onClick={if(customer.isNotBlank()&&job.isNotBlank()){add(Order(customer,job,total.toLongOrNull()?:0));customer="";job="";total=""}},modifier=Modifier.fillMaxWidth().padding(vertical=10.dp)){Text("Simpan Pesanan")}; Text("Riwayat",style=MaterialTheme.typography.titleLarge) }; items(orders.reversed()){Card(Modifier.fillMaxWidth().padding(vertical=4.dp)){Column(Modifier.padding(14.dp)){Text(it.customer,style=MaterialTheme.typography.titleMedium);Text(it.job);Text("Rp ${it.total}")}}} } }

@Composable fun Calculator(m: Modifier) { var panjang by remember{mutableStateOf("")}; var lebar by remember{mutableStateOf("")}; var harga by remember{mutableStateOf("")}; val luas=(panjang.toDoubleOrNull()?:0.0)*(lebar.toDoubleOrNull()?:0.0); val estimasi=luas*(harga.toDoubleOrNull()?:0.0); LazyColumn(m.padding(18.dp)){item{Text("Kalkulator Estimasi",style=MaterialTheme.typography.headlineSmall);Text("Hitung luas × harga per m²",modifier=Modifier.padding(vertical=8.dp));OutlinedTextField(panjang,{panjang=it},label={Text("Panjang (m)")},modifier=Modifier.fillMaxWidth());OutlinedTextField(lebar,{lebar=it},label={Text("Lebar (m)")},modifier=Modifier.fillMaxWidth());OutlinedTextField(harga,{harga=it.filter(Char::isDigit)},label={Text("Harga per m² (Rp)")},modifier=Modifier.fillMaxWidth());Spacer(Modifier.height(16.dp));Card{Column(Modifier.padding(18.dp)){Text("Luas: %.2f m²".format(luas));Text("Estimasi: Rp ${estimasi.toLong()}",style=MaterialTheme.typography.titleLarge)}}}}}
