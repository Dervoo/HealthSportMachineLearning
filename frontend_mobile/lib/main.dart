import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;

void main() {
  runApp(const HealthMLApp());
}

class HealthMLApp extends StatelessWidget {
  const HealthMLApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Health-ML Optimizer',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: const LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  String get _apiBase {
    if (kIsWeb) return 'http://localhost:8000';
    try {
      if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    } catch (_) {}
    return 'http://localhost:8000';
  }

  Future<void> _login() async {
    setState(() => _isLoading = true);
    
    final url = Uri.parse('$_apiBase/auth/token');
    
    try {
      // OAuth2PasswordRequestForm expects form-data
      final response = await http.post(
        url,
        body: {
          'username': _usernameController.text,
          'password': _passwordController.text,
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final token = data['access_token'];
        
        if (mounted) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => DashboardPage(token: token),
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Błąd logowania. Sprawdź dane.')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Błąd połączenia: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Health-ML Optimizer')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.fitness_center, size: 80, color: Colors.teal),
            const SizedBox(height: 32),
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(labelText: 'Użytkownik (e-mail)'),
            ),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Hasło'),
              obscureText: true,
            ),
            const SizedBox(height: 24),
            _isLoading 
              ? const CircularProgressIndicator()
              : ElevatedButton(
                  onPressed: _login,
                  child: const Text('Zaloguj się'),
                ),
          ],
        ),
      ),
    );
  }
}

class DashboardPage extends StatelessWidget {
  final String token;
  const DashboardPage({super.key, required this.token});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => Navigator.pushReplacement(
              context, 
              MaterialPageRoute(builder: (context) => const LoginPage())
            ),
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Witaj w Optimizerze!',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildStatCard('Cel: Redukcja skóry', Icons.accessibility_new, Colors.blue),
            _buildStatCard('Białko dzisiaj: 87.5g / 180g', Icons.fastfood, Colors.orange),
            _buildStatCard('Trening: Push (A)', Icons.fitness_center, Colors.red),
            const SizedBox(height: 24),
            const Text(
              'Analizy AI (ML Engine):',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Card(
              child: ListTile(
                leading: Icon(Icons.trending_down, color: Colors.green),
                title: Text('Trend wagi: Spadkowy (-0.4kg/tydz)'),
                subtitle: Text('Prognoza: Plateau za ok. 3 tygodnie.'),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: Implement meal photo upload
        },
        child: const Icon(Icons.camera_alt),
      ),
    );
  }

  Widget _buildStatCard(String title, IconData icon, Color color) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: ListTile(
        leading: Icon(icon, color: color),
        title: Text(title),
      ),
    );
  }
}
