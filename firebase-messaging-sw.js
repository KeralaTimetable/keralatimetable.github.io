importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "AIzaSyCQQdEQPqHebt9QCDzWIvZdRUk0g-2dCLs",
    authDomain: "kerala-timetable-db.firebaseapp.com",
    databaseURL: "https://kerala-timetable-db-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "kerala-timetable-db",
    storageBucket: "kerala-timetable-db.firebasestorage.app",
    messagingSenderId: "527439836518",
    appId: "1:527439836518:web:af7725a5bf07d6a4f584a7"
});

const messaging = firebase.messaging();

// This runs in the background to catch notifications when the website is closed
messaging.onBackgroundMessage((payload) => {
    console.log('[firebase-messaging-sw.js] Received background message ', payload);
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: 'https://cdn-icons-png.flaticon.com/512/3234/3234972.png'
    };
    self.registration.showNotification(notificationTitle, notificationOptions);
});
