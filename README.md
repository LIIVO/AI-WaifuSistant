<h1 align="center"> AI-WaifuSistant </h1>

# Kilas

Proyek ini dikembangkan berdasarkan [AI Waifu (VTuber)](https://github.com/JarikDem-Bot/ai-waifu) yang akan diimplementasikan dalam perangkat IoT berbasis Arduino. Berfungsi sebagai asisten suara dengan wujud karakter anime, memberikan pengalaman interaksi langsung dengan karakter anime.

## Fitur

- 🎤 **Interaksi Suara:** Berbicaralah dengan AI Waifu Anda dan dapatkan respons secara instan (hampir seketika).
    - Whisper - layanan pengenalan suara berbayar dari OpenAI.
    - Google sr - alternatif pengenalan suara gratis.
    - Konsol - jika Anda tidak ingin menggunakan mikrofon, cukup ketik perintah melalui keyboard.

- 🤖 **Integrasi Chatbot AI:** Percakapan ditenagai oleh chatbot AI untuk interaksi yang menarik dan dinamis.
    - *'gpt-3.5-turbo'* dari OpenAI atau model lain yang tersedia.
    - Berkas berisi deskripsi kepribadian dan perilaku.
    - Mampu mengingat pesan-pesan sebelumnya.

- 📢 **Text-to-Speech:** Dengarkan respons AI Waifu Anda dengan suara, menciptakan pengalaman yang mendalam.
    - Google tts - solusi gratis dan sederhana.
    - ElevenLabs - hasil luar biasa dengan berbagai pilihan suara.
    - Konsol - respons teks ditampilkan di konsol (model VTube hanya diam).

- 🌐 **Integrasi dengan VTube Studio:** Hubungkan AI Waifu Anda ke VTube Studio untuk interaksi yang lebih nyata dan menarik secara visual.
    - Sinkronisasi bibir saat berbicara.

## Instalasi

Untuk menjalankan proyek ini, Anda memerlukan:
1. Instal Python 3.10.5 jika belum terinstal.
2. Clone repositori dengan menjalankan `git clone https://github.com/LIIVO/AI-WaifuSistant.git`
3. Instal paket Python yang diperlukan dengan menjalankan `pip install -r requirements.txt` di direktori proyek.
4. Buat berkas `.env` di dalam direktori proyek dan masukkan kunci API Anda.
    <details>
      <summary>Template .env</summary>
      
      ```shell
      OPENAI_API_KEY='KUNCI_API_OPEN_AI_ANDA'
      ELEVENLABS_API_KEY='KUNCI_API_ELEVENLABS_ANDA'
      ```
    </details>
    
5. Instal [VB-Cable](https://vb-audio.com/Cable/)
6. Instal dan atur [VTube Studio](https://store.steampowered.com/app/1325860/VTube_Studio/)
    <details>
      <summary>Pengaturan:</summary>
      
      - Pilih `CABLE Output` sebagai mikrofon. Aktifkan `Preview microphone audio` untuk mendengar jawaban Waifu Anda.

        <img src='https://github.com/JarikDem-Bot/ai-waifu/assets/73791422/a38f8b45-44f3-4b4d-9626-2f3c812b8ba2' width='50%'>

      - Pilih input dan output untuk `Mouth Open`. Opsional, Anda dapat mengatur "breathing" untuk gerakan diam.

        <img src='https://github.com/JarikDem-Bot/ai-waifu/assets/73791422/4e7341b1-91a8-48f9-94e4-b5669163c89b' width='50%'>

    </details>

7. Atur konfigurasi yang diperlukan di `main.py` dalam fungsi `waifu.initialize`.
    <details>
      <summary>Argumen:</summary>
      
      - `user_input_service` (str) - cara untuk berinteraksi dengan Waifu.
          - `"whisper"` - layanan Whisper dari OpenAI untuk pengenalan suara; berbayar, membutuhkan kunci API OpenAI.
          - `"google"` - layanan pengenalan suara Google gratis.
          - `"console"` - masukkan perintah melalui konsol (gratis).
          - `None` atau tidak disebutkan - nilai default adalah `"whisper"`.
      - `stt_duration` (float) - durasi maksimum (dalam detik) untuk pengenalan suara. Default: `0.5`.
      - `mic_index` (int) - indeks perangkat mikrofon untuk input suara. Default: mikrofon utama.

      - `chatbot_service` (str) - layanan untuk menghasilkan respons.
          - `"openai"` - layanan teks OpenAI; berbayar, membutuhkan kunci API OpenAI.
          - `"test"` - pesan prewritten untuk pengujian.
          - `None` atau tidak disebutkan - nilai default adalah `"openai"`.
      - `chatbot_model` (str) - model untuk teks. Daftar tersedia dapat dilihat [di sini](https://platform.openai.com/docs/models/overview). Default: `"gpt-3.5-turbo"`.
      - `chatbot_temperature` (float) - tingkat kreativitas teks yang dihasilkan. Default: `0.5`.
      - `personality_file` (str) - path relatif ke berkas teks kepribadian Waifu. Default: `"personality.txt"`.
        
      - `tts_service` (str) - layanan text-to-speech.
          - `"google"` - Google tts gratis dengan suara sederhana.
          - `"elevenlabs"` - ElevenLabs tts berkualitas tinggi; berbayar, membutuhkan kunci API ElevenLabs.
          - `"console"` - respons teks hanya dicetak di konsol (gratis).
          - `None` atau tidak disebutkan - nilai default adalah `"google"`.
      - `output_device` - (int) ID perangkat output atau (str) nama perangkat output. Untuk VB-Cable, pilih perangkat dengan awalan `CABLE Input (VB-Audio Virtual`.
      - `tts_voice` (str) - nama suara ElevenLabs. Default: `"Elli"`.
      - `tts_model` (str) - model ElevenLabs. Rekomendasi: `"eleven_monolingual_v1"` atau `"eleven_multilingual_v1"`. Default: `"eleven_monolingual_v1"`.

    </details>

8. Jalankan proyek dengan menjalankan `python main.py` di direktori proyek.

<br>

> <picture>
>   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/warning.svg">
>   <img alt="Warning" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/warning.svg">
> </picture><br>
>
> Bergantung pada mode input yang dipilih, program dapat mengirimkan semua suara yang direkam atau data lain ke pihak ketiga seperti: Google (stt, tts), OpenAI (stt, text generation), ElevenLabs (tts).

## Lisensi

[MIT](/LICENSE)
