import pandas as pd

# Define the quiz questions data
questions_data = [
    # Food & Drinks
    {
        "Language": "Malay",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "epal",
        "Options": "a) Sebuah jenis daging;b) Sebuah sayur berwarna kuning;c) Sebuah minuman;d) Sebuah buah berwarna merah atau hijau",
        "Correct Answer": "d) Sebuah buah berwarna merah atau hijau"
    },
    {
        "Language": "Malay",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "pisang",
        "Options": "a) Sebuah buah panjang berwarna kuning;b) Sebuah jenis roti;c) Sebuah sayur berwarna merah;d) Sebuah minuman manis",
        "Correct Answer": "a) Sebuah buah panjang berwarna kuning"
    },
    {
        "Language": "Malay",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "air",
        "Options": "a) Cecair yang jelas untuk diminum;b) Sebuah jenis daging;c) Sebuah makanan panas;d) Sebuah buah",
        "Correct Answer": "a) Cecair yang jelas untuk diminum"
    },
    {
        "Language": "Malay",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "roti",
        "Options": "a) Sebuah buah manis;b) Makanan yang diperbuat daripada tepung dan dibakar;c) Sebuah jenis sayur;d) Minuman sejuk",
        "Correct Answer": "b) Makanan yang diperbuat daripada tepung dan dibakar"
    },
    {
        "Language": "Malay",
        "Category": "Food & Drinks",
        "Difficulty": "beginner",
        "Question": "susu",
        "Options": "a) Sebuah buah;b) Sebuah jenis daging;c) Minuman berwarna putih dari lembu;d) Makanan manis",
        "Correct Answer": "c) Minuman berwarna putih dari lembu"
    },
    # Animals
    {
        "Language": "Malay",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "anjing",
        "Options": "a) Haiwan peliharaan yang biasa menyalak;b) Sebuah burung yang boleh terbang;c) Sebuah kucing besar;d) Ikan di laut",
        "Correct Answer": "a) Haiwan peliharaan yang biasa menyalak"
    },
    {
        "Language": "Malay",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "kucing",
        "Options": "a) Ikan;b) Haiwan peliharaan yang kecil dan mengeluarkan bunyi 'meow';c) Haiwan besar yang mengaum;d) Burung yang bernyanyi",
        "Correct Answer": "b) Haiwan peliharaan yang kecil dan mengeluarkan bunyi 'meow'"
    },
    {
        "Language": "Malay",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "burung",
        "Options": "a) Haiwan besar yang berenang;b) Haiwan dengan sayap yang boleh terbang;c) Haiwan laut;d) Serangga kecil",
        "Correct Answer": "b) Haiwan dengan sayap yang boleh terbang"
    },
    {
        "Language": "Malay",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "ikan",
        "Options": "a) Burung yang terbang;b) Haiwan yang hidup di dalam air;c) Serangga;d) Haiwan besar yang hidup di darat",
        "Correct Answer": "b) Haiwan yang hidup di dalam air"
    },
    {
        "Language": "Malay",
        "Category": "Animals",
        "Difficulty": "beginner",
        "Question": "kuda",
        "Options": "a) Haiwan peliharaan seperti kucing;b) Haiwan besar yang digunakan untuk menunggang;c) Haiwan laut;d) Burung terbang",
        "Correct Answer": "b) Haiwan besar yang digunakan untuk menunggang"
    },
    # Everyday Objects
    {
        "Language": "Malay",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "buku",
        "Options": "a) Kasut;b) Minuman;c) Sesuatu yang anda baca dengan muka surat;d) Makanan",
        "Correct Answer": "c) Sesuatu yang anda baca dengan muka surat"
    },
    {
        "Language": "Malay",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "pen",
        "Options": "a) Tempat duduk;b) Alat untuk menulis;c) Pakaian;d) Makanan",
        "Correct Answer": "b) Alat untuk menulis"
    },
    {
        "Language": "Malay",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "kerusi",
        "Options": "a) Perabot untuk duduk;b) Makanan;c) Alat untuk menulis;d) Beg",
        "Correct Answer": "a) Perabot untuk duduk"
    },
    {
        "Language": "Malay",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "beg",
        "Options": "a) Sesuatu yang digunakan untuk membawa barang;b) Makanan;c) Tempat tidur;d) Minuman",
        "Correct Answer": "a) Sesuatu yang digunakan untuk membawa barang"
    },
    {
        "Language": "Malay",
        "Category": "Objects",
        "Difficulty": "beginner",
        "Question": "kunci",
        "Options": "a) Minuman;b) Pakaian;c) Jenis buah;d) Alat kecil untuk membuka kunci",
        "Correct Answer": "d) Alat kecil untuk membuka kunci"
    },
    # Family & People
    {
        "Language": "Malay",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "ibu",
        "Options": "a) Ibu perempuan;b) Teman;c) Adik lelaki;d) Ayah lelaki",
        "Correct Answer": "a) Ibu perempuan"
    },
    {
        "Language": "Malay",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "bapa",
        "Options": "a) Ayah lelaki;b) Guru;c) Ibu perempuan;d) Kakak",
        "Correct Answer": "a) Ayah lelaki"
    },
    {
        "Language": "Malay",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "adik lelaki",
        "Options": "a) Teman;b) Lelaki yang lebih muda dalam keluarga;c) Ibu;d) Perempuan yang lebih muda",
        "Correct Answer": "b) Lelaki yang lebih muda dalam keluarga"
    },
    {
        "Language": "Malay",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "kakak",
        "Options": "a) Guru;b) Lelaki yang lebih tua;c) Ibu;d) Perempuan yang lebih tua dalam keluarga",
        "Correct Answer": "d) Perempuan yang lebih tua dalam keluarga"
    },
    {
        "Language": "Malay",
        "Category": "Family",
        "Difficulty": "beginner",
        "Question": "teman",
        "Options": "a) Ahli keluarga;b) Guru;c) Seseorang yang anda suka dan bersama;d) Orang yang tidak dikenali",
        "Correct Answer": "c) Seseorang yang anda suka dan bersama"
    },
    # Colors
    {
        "Language": "Malay",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "Warna epal",
        "Options": "a) Kuning;b) Merah atau hijau;c) Hitam;d) Biru",
        "Correct Answer": "b) Merah atau hijau"
    },
    {
        "Language": "Malay",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "Warna matahari",
        "Options": "a) Hijau;b) Kuning;c) Coklat;d) Ungu",
        "Correct Answer": "b) Kuning"
    },
    {
        "Language": "Malay",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "Warna rumput",
        "Options": "a) Putih;b) Merah;c) Hijau;d) Biru",
        "Correct Answer": "c) Hijau"
    },
    {
        "Language": "Malay",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "Warna langit pada hari yang cerah",
        "Options": "a) Hitam;b) Biru;c) Oren;d) Merah jambu",
        "Correct Answer": "b) Biru"
    },
    {
        "Language": "Malay",
        "Category": "Colors",
        "Difficulty": "beginner",
        "Question": "Warna salji",
        "Options": "a) Putih;b) Biru;c) Merah;d) Kuning",
        "Correct Answer": "a) Putih"
    },
    # Numbers
    {
        "Language": "Malay",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "satu",
        "Options": "a) 1;b) 2;c) 4;d) 3",
        "Correct Answer": "a) 1"
    },
    {
        "Language": "Malay",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "lima",
        "Options": "a) 8;b) 7;c) 5;d) 6",
        "Correct Answer": "c) 5"
    },
    {
        "Language": "Malay",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "sepuluh",
        "Options": "a) 12;b) 11;c) 10;d) 9",
        "Correct Answer": "c) 10"
    },
    {
        "Language": "Malay",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "tiga",
        "Options": "a) 4;b) 5;c) 6;d) 3",
        "Correct Answer": "d) 3"
    },
    {
        "Language": "Malay",
        "Category": "Numbers",
        "Difficulty": "beginner",
        "Question": "tujuh",
        "Options": "a) 10;b) 7;c) 9;d) 8",
        "Correct Answer": "b) 7"
    },
    # Clothing
    {
        "Language": "Malay",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "baju",
        "Options": "a) Topi;b) Pakaian yang dipakai pada bahagian atas badan;c) Kasut;d) Makanan",
        "Correct Answer": "b) Pakaian yang dipakai pada bahagian atas badan"
    },
    {
        "Language": "Malay",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "kasut",
        "Options": "a) Beg;b) Makanan;c) Pakaian yang dipakai pada kaki;d) Pakaian",
        "Correct Answer": "c) Pakaian yang dipakai pada kaki"
    },
    {
        "Language": "Malay",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "topi",
        "Options": "a) Beg;b) Kasut;c) Pakaian yang dipakai pada kepala;d) Pakaian untuk kaki",
        "Correct Answer": "c) Pakaian yang dipakai pada kepala"
    },
    {
        "Language": "Malay",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "seluar",
        "Options": "a) Minuman;b) Topi;c) Makanan;d) Pakaian untuk bahagian bawah badan",
        "Correct Answer": "d) Pakaian untuk bahagian bawah badan"
    },
    {
        "Language": "Malay",
        "Category": "Clothing",
        "Difficulty": "beginner",
        "Question": "kebaya",
        "Options": "a) Kasut;b) Topi;c) Pakaian tradisional untuk perempuan;d) Beg",
        "Correct Answer": "c) Pakaian tradisional untuk perempuan"
    },
    # Actions
    {
        "Language": "Malay",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "lari",
        "Options": "a) Makan;b) Menulis;c) Tidur;d) Bergerak cepat dengan kaki",
        "Correct Answer": "d) Bergerak cepat dengan kaki"
    },
    {
        "Language": "Malay",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "makan",
        "Options": "a) Lari;b) Menyumbat makanan ke dalam mulut dan menelannya;c) Tidur;d) Minum",
        "Correct Answer": "b) Menyumbat makanan ke dalam mulut dan menelannya"
    },
    {
        "Language": "Malay",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "minum",
        "Options": "a) Makan;b) Tidur;c) Mengambil cecair ke dalam mulut;d) Menulis",
        "Correct Answer": "c) Mengambil cecair ke dalam mulut"
    },
    {
        "Language": "Malay",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "tidur",
        "Options": "a) Lari;b) Membaca;c) Menutup mata dan berehat;d) Makan",
        "Correct Answer": "c) Menutup mata dan berehat"
    },
    {
        "Language": "Malay",
        "Category": "Actions",
        "Difficulty": "beginner",
        "Question": "baca",
        "Options": "a) Tidur;b) Minum;c) Lari;d) Melihat dan memahami perkataan",
        "Correct Answer": "d) Melihat dan memahami perkataan"
    },
    # Places
    {
        "Language": "Malay",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "sekolah",
        "Options": "a) Tempat untuk pelajar belajar;b) Tempat berenang;c) Makanan;d) Tempat tidur",
        "Correct Answer": "a) Tempat untuk pelajar belajar"
    },
    {
        "Language": "Malay",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "rumah",
        "Options": "a) Sekolah;b) Taman;c) Tempat orang tinggal;d) Restoran",
        "Correct Answer": "c) Tempat orang tinggal"
    },
    {
        "Language": "Malay",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "taman",
        "Options": "a) Sekolah;b) Tempat dengan rumput, pokok, dan taman permainan;c) Hospital;d) Kedai",
        "Correct Answer": "b) Tempat dengan rumput, pokok, dan taman permainan"
    },
    {
        "Language": "Malay",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "hospital",
        "Options": "a) Sekolah;b) Restoran;c) Taman;d) Tempat orang sakit mendapatkan rawatan",
        "Correct Answer": "d) Tempat orang sakit mendapatkan rawatan"
    },
    {
        "Language": "Malay",
        "Category": "Places",
        "Difficulty": "beginner",
        "Question": "restoran",
        "Options": "a) Sekolah;b) Tempat untuk makan;c) Hospital;d) Taman",
        "Correct Answer": "b) Tempat untuk makan"
    },
    # Time & Days
    {
        "Language": "Malay",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "pagi",
        "Options": "a) Waktu malam;b) Waktu petang;c) Tengah hari;d) Bahagian awal hari (sebelum tengah hari)",
        "Correct Answer": "d) Bahagian awal hari (sebelum tengah hari)"
    },
    {
        "Language": "Malay",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "malam",
        "Options": "a) Waktu pagi;b) Waktu ketika hari gelap;c) Waktu tengah hari;d) Waktu petang",
        "Correct Answer": "b) Waktu ketika hari gelap"
    },
    {
        "Language": "Malay",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "Isnin",
        "Options": "a) Hari terakhir dalam minggu;b) Hari pertama dalam minggu;c) Hari pertama dalam bulan;d) Hari pertama dalam tahun",
        "Correct Answer": "b) Hari pertama dalam minggu"
    },
    {
        "Language": "Malay",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "hari ini",
        "Options": "a) Minggu depan;b) Semalam;c) Hari semasa yang sedang berlaku;d) Esok",
        "Correct Answer": "c) Hari semasa yang sedang berlaku"
    },
    {
        "Language": "Malay",
        "Category": "Time & Days",
        "Difficulty": "beginner",
        "Question": "tahun",
        "Options": "a) Sehari;b) Sebulan;c) Seminggu;d) 12 bulan (365 hari)",
        "Correct Answer": "d) 12 bulan (365 hari)"
    }
]

# Create DataFrame
df = pd.DataFrame(questions_data)

# Save to Excel
df.to_excel('malay_quiz_questions.xlsx', index=False)
print("Excel file 'malay_quiz_questions.xlsx' has been created successfully with 50 questions.") 