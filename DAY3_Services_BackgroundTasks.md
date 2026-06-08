# 📱 DAY 3: SERVICES & BACKGROUND TASKS

## 🎯 Topics Covered
1. **Service Basics**
2. **Types of Services**
3. **Service Lifecycle**
4. **Foreground Services**
5. **WorkManager (Modern Approach)**
6. **Background Tasks Best Practices**

---

## 🔧 WHAT IS A SERVICE?

### Definition
A **Service** is an Android component that runs in the background **WITHOUT a UI**. It continues running even when the user switches apps or screen goes off.

### Key Characteristics
- ✅ Runs in background without UI
- ✅ Can run indefinitely (if not killed)
- ✅ Survives app closure (depends on type)
- ✅ Uses main thread by default (need coroutines/threads for heavy work)
- ✅ Declared in AndroidManifest.xml

### Why Use Services?

| Task | Need Service? |
|------|---|
| Play music while screen off | ✅ Yes |
| Download large file in background | ✅ Yes (better: WorkManager) |
| Track GPS location (Emergency) | ✅ Yes (Foreground) |
| Sync data to server periodically | ✅ Yes (better: WorkManager) |
| Update UI every second | ❌ No, use ViewModel + LiveData |
| One-time background operation | ❌ No, use WorkManager or IntentService |

---

## 📊 3 TYPES OF SERVICES

### Type 1️⃣: STARTED SERVICE ⭐⭐⭐

**How it works:**
- Start service with `startService(intent)`
- Runs indefinitely until explicitly stopped
- No built-in connection between activity and service

**Lifecycle:**
```
startService()
    ↓
onCreate() (once)
    ↓
onStartCommand() (every time startService called)
    ↓
[Running in background]
    ↓
stopService() or stopSelf()
    ↓
onDestroy()
```

**Used For:**
- Music player
- GPS tracking (Emergency SOS)
- Background uploads/downloads
- Continuous data processing

**Return Values:**
```kotlin
override fun onStartCommand(...): Int {
    return START_STICKY  // Restart if killed
    // return START_STICKY_COMPATIBILITY
    // return START_NOT_STICKY  // Don't restart
}
```

| Return Value | Behavior |
|---|---|
| `START_STICKY` | Service restarted if killed, intent = null |
| `START_STICKY_COMPATIBILITY` | Older version of START_STICKY |
| `START_NOT_STICKY` | Service NOT restarted if killed |
| `START_REDELIVER_INTENT` | Service restarted with last intent |

---

### Type 2️⃣: BOUND SERVICE

**How it works:**
- Client (Activity/Fragment) **connects** to service
- **Two-way communication** between client and service
- Service lives as long as client is bound

**Lifecycle:**
```
bindService()
    ↓
onCreate() (once)
    ↓
onBind() ← Return IBinder for communication
    ↓
[Service bound to client, can communicate]
    ↓
unbindService()
    ↓
onDestroy()
```

**Used For:**
- Music player with controls from activity
- GPS service with position updates
- Utility service with helper methods

**Example:**
```kotlin
// Service
inner class MusicBinder : Binder() {
    fun getService(): MusicService = this@MusicService
}

override fun onBind(intent: Intent?): IBinder? {
    return MusicBinder()
}

fun play() { /* ... */ }
fun pause() { /* ... */ }

// Activity
private var musicService: MusicService? = null
private var isBound = false

private val connection = object : ServiceConnection {
    override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
        val binder = service as MusicService.MusicBinder
        musicService = binder.getService()
        isBound = true
    }
    
    override fun onServiceDisconnected(name: ComponentName?) {
        isBound = false
    }
}

fun startPlaying() {
    if (isBound) {
        musicService?.play()
    }
}
```

---

### Type 3️⃣: INTENT SERVICE (Deprecated - Use WorkManager)

**How it works:**
- Automatically handles one task on background thread
- Automatically stops after task completes
- Good for one-time background operations

**Example:**
```kotlin
class DownloadService : IntentService("DownloadService") {
    override fun onHandleIntent(intent: Intent?) {
        // Long-running task on background thread
        downloadFile()
        // Service automatically stops
    }
}
```

**Status:** ⚠️ Deprecated, use `WorkManager` instead

---

## 🔄 SERVICE LIFECYCLE

### Complete Flow
```
        onCreate()
            ↓
    onStartCommand()  (called multiple times)
            ↓
    [SERVICE RUNNING]
            ↓
    onDestroy()
            ↓
    [SERVICE STOPPED]
```

### onCreate()
- **Called:** Once when service created
- **Do:** Initialize resources, set up connections
- **Example:**
  ```kotlin
  override fun onCreate() {
      super.onCreate()
      mediaPlayer = MediaPlayer()
  }
  ```

### onStartCommand()
- **Called:** Every time `startService()` is called
- **Do:** Handle the start request, implement long-running task
- **Return:** One of START_STICKY, START_NOT_STICKY, etc.
- **Example:**
  ```kotlin
  override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
      val action = intent?.action
      when (action) {
          "PLAY" -> playMusic()
          "PAUSE" -> pauseMusic()
          "STOP" -> stopMusic()
      }
      return START_STICKY
  }
  ```

### onDestroy()
- **Called:** When service is destroyed
- **Do:** Clean up resources, release locks
- **Example:**
  ```kotlin
  override fun onDestroy() {
      super.onDestroy()
      mediaPlayer?.release()
  }
  ```

### onBind()
- **Called:** When client binds to service (Bound Service only)
- **Return:** IBinder for communication
- **If not used:** Return `null`

---

## 🔔 FOREGROUND SERVICE (Android 8.0+) ⭐⭐⭐

**What:** Service with persistent notification visible to user

**Why:** 
- Cannot be swiped away
- User knows app is running
- Required for location tracking, music player

**Your PatientmangSystemApp uses this for Emergency SOS!**

### Required Steps:

#### 1️⃣ Create NotificationChannel (Required API 26+)
```kotlin
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    val channel = NotificationChannel(
        "location_channel",
        "Location Tracking",
        NotificationManager.IMPORTANCE_DEFAULT
    )
    val notificationManager = getSystemService(NotificationManager::class.java)
    notificationManager.createNotificationChannel(channel)
}
```

#### 2️⃣ Create Notification
```kotlin
val notification = NotificationCompat.Builder(this, "location_channel")
    .setSmallIcon(R.drawable.ic_location)
    .setContentTitle("Location Tracking")
    .setContentText("Emergency SOS active")
    .setOngoing(true)  // Can't be swiped
    .build()
```

#### 3️⃣ Start Foreground Service
```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    startForeground(1, notification)  // Show notification
    startLocationTracking()
    return START_STICKY
}
```

#### 4️⃣ Declare in AndroidManifest.xml
```xml
<service
    android:name=".services.LocationService"
    android:enabled="true"
    android:exported="false"
    android:foregroundServiceType="location" />

<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
```

---

## ⚠️ ANDROID 12+ RESTRICTIONS

Starting Android 12, background services are heavily restricted:

| Restriction | Impact |
|---|---|
| **Can't run indefinitely** | Service stops after 10 min in background |
| **Must use WorkManager** | For periodic tasks |
| **Foreground Service required** | For long-running tasks with notification |
| **Explicit permissions** | `FOREGROUND_SERVICE` permission needed |

**Solution:**
- ✅ Use **WorkManager** for periodic/deferred tasks
- ✅ Use **Foreground Service** for immediate long-running tasks
- ❌ Don't rely on `START_STICKY` for indefinite running

---

## 🔨 MODERN APPROACH: WorkManager ⭐⭐⭐⭐⭐

**Better than Service for most background tasks**

### Why WorkManager?
- ✅ Handles battery optimization automatically
- ✅ Respects system constraints
- ✅ Works across Android versions
- ✅ Handles failed retries automatically
- ✅ Schedules tasks reliably

### Step 1: Create Worker
```kotlin
class LocationWorker(
    context: Context,
    params: WorkerParameters
) : Worker(context, params) {
    
    override fun doWork(): Result {
        return try {
            val location = getLastKnownLocation()
            sendLocationToServer(location)
            Result.success()
        } catch (e: Exception) {
            Result.retry()  // Retry later
        }
    }
}
```

### Step 2: Schedule Work
```kotlin
// One-time work
val work = OneTimeWorkRequestBuilder<LocationWorker>()
    .setInitialDelay(5, TimeUnit.MINUTES)
    .build()
WorkManager.getInstance(context).enqueue(work)

// Periodic work (every 15 minutes)
val periodicWork = PeriodicWorkRequestBuilder<LocationWorker>(
    15, TimeUnit.MINUTES
).build()
WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "location_work",
    ExistingPeriodicWorkPolicy.KEEP,
    periodicWork
)
```

### Step 3: Check Status
```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workId)
    .observe(this) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.RUNNING -> Log.d("Work", "Running")
            WorkInfo.State.SUCCEEDED -> Log.d("Work", "Done")
            WorkInfo.State.FAILED -> Log.d("Work", "Failed")
            else -> {}
        }
    }
```

---

## 📊 SERVICE vs WORKMANAGER vs COROUTINES

| Feature | Service | WorkManager | Coroutines |
|---------|---------|-------------|-----------|
| **Runs after app closes?** | ✅ Yes | ✅ Yes | ❌ No |
| **Battery aware?** | ❌ No | ✅ Yes | N/A |
| **Automatic retry?** | ❌ No | ✅ Yes | ❌ No |
| **Notification required?** | ✅ (Foreground) | ❌ No | N/A |
| **Use for** | Long tasks | Periodic work | UI updates |
| **Example** | GPS tracking | Sync every 15min | Network call |

---

## 💻 START/STOP SERVICE

### Start Service
```kotlin
// Android 8.0+
val intent = Intent(this, MyService::class.java)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent)
} else {
    startService(intent)
}
```

### Stop Service
```kotlin
// From Activity
val intent = Intent(this, MyService::class.java)
stopService(intent)

// From Service itself
stopSelf()
stopSelf(startId)
```

### Pass Data to Service
```kotlin
val intent = Intent(this, MyService::class.java)
intent.action = "PLAY_MUSIC"
intent.putExtra("song_id", 42)
startService(intent)

// In Service
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    val action = intent?.action
    val songId = intent?.getIntExtra("song_id", -1)
    // ...
    return START_STICKY
}
```

---

## ⚡ QUICK REFERENCE

| Task | Code |
|---|---|
| **Create Service** | `class MyService : Service()` |
| **Declare in manifest** | `<service android:name=".MyService" />` |
| **Start service** | `startService(Intent(this, MyService::class.java))` |
| **Stop service** | `stopService(intent)` |
| **Foreground service** | `startForeground(id, notification)` |
| **Broadcast to listeners** | `sendBroadcast(intent)` |
| **Use WorkManager** | `WorkManager.getInstance(context).enqueue(work)` |

---

## 🎯 BEST PRACTICES

✅ **DO:**
- Use WorkManager for periodic tasks (Android 12+)
- Use Foreground Service with notification for long-running tasks
- Handle service destruction in onDestroy()
- Stop service when no longer needed
- Test on real device (emulator behaves differently)
- Use coroutines/threads for heavy work (don't block main thread)

❌ **DON'T:**
- Keep service running indefinitely (Android 12+ doesn't allow)
- Block main thread with heavy operations
- Forget to declare service in AndroidManifest.xml
- Forget notification channel for Foreground Service
- Use deprecated IntentService (use WorkManager)
- Create multiple service instances (they share one process)

---

## 📱 YOUR PROJECT APPLICATION

**PatientmangSystemApp - Emergency SOS:**
```kotlin
override fun activateSOS() {
    val intent = Intent(this, LocationService::class.java)
    
    // Start foreground service (visible notification)
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        startForegroundService(intent)
    } else {
        startService(intent)
    }
}

override fun onDestroy() {
    super.onDestroy()
    val intent = Intent(this, LocationService::class.java)
    stopService(intent)
}
```

**Service:**
```kotlin
class LocationService : Service() {
    override fun onCreate() {
        super.onCreate()
        // Initialize location client
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundNotification()
        startLocationTracking()
        return START_STICKY
    }
}
```

---

## 🔗 AndroidManifest.xml Requirements

```xml
<!-- Declare Service -->
<service android:name=".services.LocationService"
    android:exported="false"
    android:foregroundServiceType="location" />

<!-- Required Permissions -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.INTERNET" />
```

---

**Day 3 Summary:** Services run background tasks without UI. Use WorkManager for modern apps, Foreground Service for immediate tasks! 🎉
