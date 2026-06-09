# 📱 DAY 4: DATA STORAGE (SharedPreferences, DataStore & Room Database)

## 🎯 Topics Covered
1. **SharedPreferences (Legacy)**
2. **DataStore (Modern Alternative - RECOMMENDED)**
3. **Room Database**
4. **Comparison & Best Practices**

---

## 🔄 EVOLUTION OF DATA STORAGE

```
SharedPreferences (2008) 
    ↓ (Synchronous, thread-unsafe)
DataStore (2020) ← MODERN & RECOMMENDED ⭐⭐⭐
    ↓ (Async, Kotlin-first, type-safe)
Room Database (2017)
    ↓ (For complex structured data)
```

---

## ❌ WHY SharedPreferences IS OUTDATED

### Problems with SharedPreferences:

1. **Thread-Unsafe** ⚠️
   - Can cause data corruption if accessed from multiple threads
   - No synchronization

2. **Synchronous Blocking** ⚠️
   - `commit()` blocks main thread
   - UI freezes during save
   - Bad user experience

3. **No Type Safety** ⚠️
   - Use `getString()`, `getInt()` - error-prone
   - Easy to store/retrieve wrong type
   - Crashes at runtime if type mismatch

4. **No Lifecycle Awareness** ⚠️
   - No automatic cleanup
   - Manual null handling required

5. **Complex Data Issues** ⚠️
   - Hard to serialize complex objects
   - No encryption built-in
   - Limited to primitives

### Example of SharedPreferences Problems:

```kotlin
❌ BAD - Blocks UI thread
val prefs = context.getSharedPreferences("app", Context.MODE_PRIVATE)
prefs.edit().putString("user_name", "John").commit()  // Freezes UI!

❌ RISKY - Thread-unsafe
Thread {
    prefs.edit().putString("data", "value").apply()  // Potential data loss
}.start()

❌ ERROR-PRONE - Type mismatch
prefs.putString("age", "25")  // Stored as string
val age = prefs.getInt("age", 0)  // Trying to read as int → Returns default 0!
```

---

## ✅ DATASTORE - THE MODERN SOLUTION ⭐⭐⭐⭐⭐

### **What is DataStore?**

Google's recommended replacement for SharedPreferences:
- ✅ Fully asynchronous (suspend functions)
- ✅ Thread-safe using Kotlin coroutines
- ✅ Type-safe (compile-time checking)
- ✅ Kotlin-first (Flows, coroutines)
- ✅ ACID transactions
- ✅ Built-in migration from SharedPreferences

### **2 Types of DataStore**

#### **Type 1: Preferences DataStore** (Simple key-value, like SharedPreferences)
```kotlin
val dataStore: DataStore<Preferences> = context.createDataStore(
    name = "app_preferences"
)
```

#### **Type 2: Proto DataStore** (Type-safe, structured data)
```kotlin
val dataStore: DataStore<UserPreferences> = context.createDataStore(
    fileName = "user_prefs.pb",
    serializer = UserPreferencesSerializer
)
```

**We'll cover Preferences DataStore (easier & common)**

---

## 📦 SETUP DATASTORE

### **Step 1: Add Dependencies**

```gradle
dependencies {
    // DataStore (Preferences)
    implementation "androidx.datastore:datastore-preferences:1.0.0"
    
    // Coroutines
    implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3"
    
    // Lifecycle
    implementation "androidx.lifecycle:lifecycle-runtime-ktx:2.6.2"
}
```

---

## 💻 PREFERENCES DATASTORE COMPLETE EXAMPLE

### **Step 1: Create DataStore Manager**

```kotlin
package com.example.patientapp.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

// Create DataStore instance
private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "app_preferences"
)

class UserPreferencesManager(context: Context) {
    
    private val dataStore = context.dataStore
    
    // Define keys
    companion object {
        val USER_NAME = stringPreferencesKey("user_name")
        val USER_EMAIL = stringPreferencesKey("user_email")
        val USER_ID = intPreferencesKey("user_id")
        val IS_LOGGED_IN = booleanPreferencesKey("is_logged_in")
        val AUTH_TOKEN = stringPreferencesKey("auth_token")
        val THEME = stringPreferencesKey("theme")
    }
    
    // ✅ Async read - Returns Flow (real-time updates!)
    val userName: Flow<String> = dataStore.data
        .map { preferences ->
            preferences[USER_NAME] ?: "Unknown"
        }
    
    val userEmail: Flow<String> = dataStore.data
        .map { preferences ->
            preferences[USER_EMAIL] ?: ""
        }
    
    val userId: Flow<Int> = dataStore.data
        .map { preferences ->
            preferences[USER_ID] ?: -1
        }
    
    val isLoggedIn: Flow<Boolean> = dataStore.data
        .map { preferences ->
            preferences[IS_LOGGED_IN] ?: false
        }
    
    // ✅ Async write - Suspend function (non-blocking!)
    suspend fun saveUserInfo(name: String, email: String, id: Int) {
        dataStore.edit { preferences ->
            preferences[USER_NAME] = name
            preferences[USER_EMAIL] = email
            preferences[USER_ID] = id
        }
    }
    
    suspend fun setLoggedIn(value: Boolean) {
        dataStore.edit { preferences ->
            preferences[IS_LOGGED_IN] = value
        }
    }
    
    suspend fun saveAuthToken(token: String) {
        dataStore.edit { preferences ->
            preferences[AUTH_TOKEN] = token
        }
    }
    
    suspend fun setTheme(theme: String) {
        dataStore.edit { preferences ->
            preferences[THEME] = theme
        }
    }
    
    suspend fun logout() {
        dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
```

---

## 🎯 USAGE IN ACTIVITY/FRAGMENT

### **Example 1: Reading Data (Observe Real-time)**

```kotlin
class LoginActivity : AppCompatActivity() {
    
    private val prefManager by lazy {
        UserPreferencesManager(this)
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)
        
        // Observe login state in real-time
        lifecycleScope.launch {
            prefManager.isLoggedIn.collect { loggedIn ->
                if (loggedIn) {
                    Log.d("Login", "User is logged in!")
                    // Navigate to home
                    startActivity(Intent(this@LoginActivity, HomeActivity::class.java))
                    finish()
                }
            }
        }
    }
}
```

### **Example 2: Writing Data (Non-blocking)**

```kotlin
class ProfileFragment : Fragment() {
    
    private val prefManager by lazy {
        UserPreferencesManager(requireContext())
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        saveButton.setOnClickListener {
            val name = nameInput.text.toString()
            val email = emailInput.text.toString()
            val id = 42
            
            // ✅ Async write - doesn't block UI!
            viewLifecycleOwner.lifecycleScope.launch {
                prefManager.saveUserInfo(name, email, id)
                Toast.makeText(requireContext(), "Saved!", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
```

### **Example 3: Complete Login Flow**

```kotlin
class LoginFragment : Fragment() {
    
    private val prefManager by lazy {
        UserPreferencesManager(requireContext())
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        loginButton.setOnClickListener {
            val email = emailInput.text.toString()
            val password = passwordInput.text.toString()
            
            // Authenticate with server
            authenticateUser(email, password) { user ->
                viewLifecycleOwner.lifecycleScope.launch {
                    // ✅ Save user info asynchronously
                    prefManager.saveUserInfo(
                        name = user.name,
                        email = user.email,
                        id = user.id
                    )
                    
                    // ✅ Save auth token
                    prefManager.saveAuthToken(user.token)
                    
                    // ✅ Set logged in flag
                    prefManager.setLoggedIn(true)
                    
                    // Navigate to home (automatic if observing isLoggedIn)
                    navController.navigate(R.id.action_to_home)
                }
            }
        }
    }
}
```

---

## 📊 SHAREDPREFERENCES vs DATASTORE

| Feature | SharedPreferences | DataStore |
|---------|---|---|
| **Thread-Safe?** | ❌ No | ✅ Yes |
| **Async/Blocking** | ❌ Synchronous (blocks UI) | ✅ Async (suspend) |
| **Type-Safe?** | ❌ No | ✅ Yes |
| **Real-time Updates** | ❌ No | ✅ Flow/LiveData |
| **Coroutines** | ❌ No | ✅ Full support |
| **ACID Transactions** | ❌ No | ✅ Yes |
| **Encryption** | ❌ No | ✅ EncryptedSharedPreferences available |
| **Modern?** | ❌ Deprecated | ✅ Recommended |
| **Easy Migration** | N/A | ✅ From SharedPreferences |

---

## ⚡ QUICK COMPARISON CODE

### ❌ OLD WAY (SharedPreferences)

```kotlin
// BLOCKS UI THREAD
val prefs = context.getSharedPreferences("app", Context.MODE_PRIVATE)
prefs.edit().putString("name", "John").commit()  // FREEZES UI! ⚠️

// NO TYPE SAFETY
prefs.putString("age", "25")
val age = prefs.getInt("age", 0)  // Returns 0, wrong type!

// NO REAL-TIME UPDATES
// Must manually refresh UI
val name = prefs.getString("name", "")
textView.text = name  // Old value shown until manually refresh
```

### ✅ NEW WAY (DataStore)

```kotlin
// ASYNC - DOESN'T BLOCK UI
viewLifecycleOwner.lifecycleScope.launch {
    prefManager.saveUserInfo("John", "john@email.com", 25)  // Non-blocking! ✅
}

// TYPE SAFE
prefManager.userName: Flow<String>  // Compile-time checking

// REAL-TIME UPDATES
prefManager.userName.collect { name ->
    textView.text = name  // Automatically updates!
}
```

---

## 🔧 MIGRATION FROM SHAREDPREFERENCES TO DATASTORE

### **Automatic Migration**

```kotlin
// DataStore automatically migrates SharedPreferences!
private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "app_preferences",
    produceMigrations = { context ->
        listOf(
            SharedPreferencesMigration(context, "old_shared_prefs_name")
        )
    }
)
```

### **Manual Migration**

```kotlin
suspend fun migrateFromSharedPreferences() {
    val oldPrefs = context.getSharedPreferences("old_name", Context.MODE_PRIVATE)
    
    dataStore.edit { newPrefs ->
        // Copy each value
        oldPrefs.all.forEach { (key, value) ->
            when (value) {
                is String -> newPrefs[stringPreferencesKey(key)] = value
                is Int -> newPrefs[intPreferencesKey(key)] = value
                is Boolean -> newPrefs[booleanPreferencesKey(key)] = value
                // ... etc
            }
        }
    }
    
    // Delete old SharedPreferences
    oldPrefs.edit().clear().commit()
}
```

---

# 💾 ROOM DATABASE (Same as Day 4)

Room is used for **complex structured data** with relationships. DataStore is for simple key-value preferences.

## **When to Use What?**

| Data Type | Use DataStore | Use Room |
|---|---|---|
| Auth token | ✅ Yes | ❌ No |
| User theme | ✅ Yes | ❌ No |
| User preferences | ✅ Yes | ❌ No |
| Patient records | ❌ No | ✅ Yes |
| Appointments list | ❌ No | ✅ Yes |
| Chat messages | ❌ No | ✅ Yes |
| Settings | ✅ Yes | ❌ No |
| Complex relationships | ❌ No | ✅ Yes |

---

## 🎯 COMPLETE MODERN ARCHITECTURE

```
┌──────────────────────────────────────────┐
│            UI Layer (Activity/Fragment)   │
│  (Observe LiveData/Flow in real-time)    │
└──────────┬───────────────────────────────┘
           │
┌──────────▼──────────────────────────────┐
│         ViewModel                        │
│  (Manages UI state & business logic)    │
└──────────┬───────────────────────────────┘
           │
    ┌──────┴───────┐
    │              │
┌───▼──────┐  ┌───▼──────────┐
│ DataStore│  │    Room DB   │
│(Prefs)   │  │(Complex data)│
└──────────┘  └──────────────┘
```

---

## 📝 COMPLETE EXAMPLE: Login with DataStore

```kotlin
// UserPreferencesManager.kt
class UserPreferencesManager(context: Context) {
    
    private val dataStore = context.dataStore
    
    companion object {
        val IS_LOGGED_IN = booleanPreferencesKey("is_logged_in")
        val USER_NAME = stringPreferencesKey("user_name")
        val AUTH_TOKEN = stringPreferencesKey("auth_token")
        val USER_ID = intPreferencesKey("user_id")
    }
    
    // Flows for real-time observation
    val isLoggedIn: Flow<Boolean> = dataStore.data.map { 
        it[IS_LOGGED_IN] ?: false 
    }
    
    val userName: Flow<String> = dataStore.data.map { 
        it[USER_NAME] ?: "" 
    }
    
    // Save login info
    suspend fun saveLoginInfo(name: String, token: String, userId: Int) {
        dataStore.edit { preferences ->
            preferences[USER_NAME] = name
            preferences[AUTH_TOKEN] = token
            preferences[USER_ID] = userId
            preferences[IS_LOGGED_IN] = true
        }
    }
    
    // Logout
    suspend fun logout() {
        dataStore.edit { preferences ->
            preferences.clear()
        }
    }
    
    // Get auth token
    suspend fun getAuthToken(): String? {
        return dataStore.data.firstOrNull()?.get(AUTH_TOKEN)
    }
}

// LoginViewModel.kt
class LoginViewModel(private val prefManager: UserPreferencesManager) : ViewModel() {
    
    fun login(email: String, password: String) {
        viewModelScope.launch {
            try {
                // Call API
                val response = apiService.login(email, password)
                
                // ✅ Save to DataStore (async, non-blocking)
                prefManager.saveLoginInfo(
                    name = response.user.name,
                    token = response.token,
                    userId = response.user.id
                )
                
                _loginSuccess.value = true
            } catch (e: Exception) {
                _loginError.value = e.message
            }
        }
    }
}

// LoginActivity.kt
class LoginActivity : AppCompatActivity() {
    
    private val prefManager by lazy { UserPreferencesManager(this) }
    private val viewModel by viewModels<LoginViewModel>()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)
        
        // Check if already logged in
        lifecycleScope.launch {
            prefManager.isLoggedIn.collect { loggedIn ->
                if (loggedIn) {
                    // Auto redirect to home
                    startActivity(Intent(this@LoginActivity, HomeActivity::class.java))
                    finish()
                }
            }
        }
        
        // Login button
        loginButton.setOnClickListener {
            val email = emailInput.text.toString()
            val password = passwordInput.text.toString()
            viewModel.login(email, password)
        }
    }
}
```

---

## ✅ BEST PRACTICES

✅ **DataStore:**
- Use for all user preferences, settings, tokens
- Always use with coroutines/suspend functions
- Observe with `.collect { }` for real-time updates
- No manual null checking (provide defaults)

✅ **Room:**
- Use for complex structured data
- Use Repository pattern for clean code
- Observe with LiveData/Flow
- Always use suspend functions for DB operations

✅ **General:**
- DataStore for all simple key-value data (MODERN)
- SharedPreferences only for backwards compatibility
- Don't block UI thread (use suspend/coroutines)
- Provide sensible defaults when reading

---

## 🚀 YOUR PROJECT APPLICATION

**PatientmangSystemApp:**
```kotlin
// DataStore: User preferences, auth token, theme
prefManager.saveAuthToken(user.token)
prefManager.isLoggedIn.collect { }

// Room: Patient records, appointments, prescriptions
patientRepository.getAllPatients()

// Firebase: Real-time sync across devices
```

---

**Day 4 Summary:** DataStore is the modern replacement for SharedPreferences! Use DataStore for preferences (async, type-safe), Room for complex data! 🎉

**Tomorrow: Day 5 - RecyclerView & Adapters** - Display lists efficiently!
