import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';

import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const HealthMLApp());
}

class HealthMLApp extends StatelessWidget {
  const HealthMLApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Health-ML Optimizer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0F0F0F),
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.teal,
          brightness: Brightness.dark,
          primary: Colors.tealAccent,
        ),
        useMaterial3: true,
      ),
      home: const LoginPage(),
    );
  }
}

// --- UTILS ---
String get _apiBase {
  if (kIsWeb) return 'http://localhost:8000';
  try {
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
  } catch (_) {}
  return 'http://localhost:8000';
}

class UserData {
  final int id;
  final String name, email, goal;
  final int targetKcal;
  final double targetProtein, waterGoal;
  UserData({
    required this.id,
    required this.name,
    required this.email,
    required this.goal,
    required this.targetKcal,
    required this.targetProtein,
    required this.waterGoal,
  });
  factory UserData.fromJson(Map<String, dynamic> json) {
    return UserData(
      id: json['id'] as int,
      name: json['name'] as String,
      email: json['email'] as String,
      goal: json['goal'] ?? "utrzymanie",
      targetKcal: (json['target_kcal'] as num).toInt(),
      targetProtein: (json['target_protein'] as num).toDouble(),
      waterGoal: (json['water_goal'] as num).toDouble(),
    );
  }
}

// --- PAGES ---
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _e = TextEditingController(), _p = TextEditingController();
  bool _l = false;
  Future<void> _login() async {
    setState(() => _l = true);
    try {
      final res = await http.post(Uri.parse('$_apiBase/auth/token'),
          body: {'username': _e.text, 'password': _p.text});
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        Navigator.pushReplacement(
            context,
            MaterialPageRoute(
                builder: (context) =>
                    DashboardContainer(token: data['access_token'])));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Błąd logowania (sprawdź dane)')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Błąd połączenia: $e')));
    } finally {
      setState(() => _l = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        body: Center(
            child: SingleChildScrollView(
                padding: const EdgeInsets.all(32),
                child: Column(children: [
                  const Icon(Icons.bolt, size: 80, color: Colors.tealAccent),
                  const Text('Health-ML',
                      style:
                          TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 48),
                  TextField(
                      controller: _e,
                      decoration: const InputDecoration(
                          labelText: 'Email', border: OutlineInputBorder())),
                  const SizedBox(height: 16),
                  TextField(
                      controller: _p,
                      decoration: const InputDecoration(
                          labelText: 'Hasło', border: OutlineInputBorder()),
                      obscureText: true,
                      onSubmitted: (_) => _login()),
                  const SizedBox(height: 32),
                  _l
                      ? const CircularProgressIndicator()
                      : SizedBox(
                          width: double.infinity,
                          height: 50,
                          child: ElevatedButton(
                              onPressed: _login,
                              child: const Text('Zaloguj się'))),
                  const SizedBox(height: 16),
                  const Text("Konto testowe: abc@gmail.com / 123",
                      style: TextStyle(color: Colors.grey, fontSize: 12)),
                  TextButton(
                      onPressed: () => Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (context) => const RegisterPage())),
                      child: const Text('Zarejestruj się'))
                ]))));
  }
}

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});
  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _n = TextEditingController(),
      _e = TextEditingController(),
      _p = TextEditingController(),
      _w = TextEditingController(text: "80");
  String _g = "Mężczyzna", _goal = "utrzymanie";
  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(title: const Text('Nowy Profil')),
        body: ListView(padding: const EdgeInsets.all(24), children: [
          TextField(controller: _n, decoration: const InputDecoration(labelText: 'Imię')),
          TextField(controller: _e, decoration: const InputDecoration(labelText: 'Email')),
          TextField(controller: _p, decoration: const InputDecoration(labelText: 'Hasło'), obscureText: true),
          TextField(controller: _w, decoration: const InputDecoration(labelText: 'Waga (kg)')),
          DropdownButtonFormField<String>(
              value: _g,
              items: ["Mężczyzna", "Kobieta"]
                  .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                  .toList(),
              onChanged: (v) => setState(() => _g = v!),
              decoration: const InputDecoration(labelText: 'Płeć')),
          DropdownButtonFormField<String>(
              value: _goal,
              items: ["redukcja", "utrzymanie", "masa"]
                  .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                  .toList(),
              onChanged: (v) => setState(() => _goal = v!),
              decoration: const InputDecoration(labelText: 'Cel')),
          const SizedBox(height: 32),
          ElevatedButton(
              onPressed: () async {
                await http.post(Uri.parse('$_apiBase/auth/register'),
                    headers: {'Content-Type': 'application/json'},
                    body: jsonEncode({
                      "name": _n.text,
                      "email": _e.text,
                      "password": _p.text,
                      "age": 25,
                      "height": 180,
                      "weight": double.parse(_w.text),
                      "gender": _g,
                      "activity": 1.55,
                      "goal": _goal
                    }));
                Navigator.pop(context);
              },
              child: const Text('Stwórz'))
        ]));
  }
}

class DashboardContainer extends StatefulWidget {
  final String token;
  const DashboardContainer({super.key, required this.token});
  @override
  State<DashboardContainer> createState() => _DashboardContainerState();
}

class _DashboardContainerState extends State<DashboardContainer> {
  int _idx = 0;
  UserData? _user;
  Map<String, dynamic> _prog = {
    "kcal": 0,
    "protein": 0.0,
    "carbs": 0.0,
    "fats": 0.0,
    "water": 0.0,
    "weight": 80.0,
    "training_log": "Rest Day"
  };
  List _meals = [];
  List _hist = [];
  bool _loading = true;
  DateTime _selectedDate = DateTime.now();

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    if (!mounted) return;
    setState(() => _loading = true);
    final auth = {'Authorization': 'Bearer ${widget.token}'};
    final dateStr = DateFormat('yyyy-MM-dd').format(_selectedDate);

    try {
      final resMe = await http.get(Uri.parse('$_apiBase/users/me'), headers: auth);
      if (resMe.statusCode == 200) {
        setState(() => _user = UserData.fromJson(jsonDecode(resMe.body)));
      }

      final resProg = await http.get(Uri.parse('$_apiBase/progress/'), headers: auth);
      if (resProg.statusCode == 200) {
        final List l = jsonDecode(resProg.body);
        _hist = l;
        final t = l.firstWhere((x) => x['date'] == dateStr, orElse: () => null);
        if (t != null) {
          setState(() => _prog = Map<String, dynamic>.from(t));
        } else {
          setState(() => _prog = {
                "date": dateStr,
                "kcal": 0,
                "protein": 0.0,
                "carbs": 0.0,
                "fats": 0.0,
                "water": 0.0,
                "weight": _hist.isNotEmpty ? (_hist.last['weight'] as num).toDouble() : 80.0,
                "training_log": "Rest Day"
              });
        }
      }

      final resMeals = await http.get(Uri.parse('$_apiBase/meals/$dateStr'), headers: auth);
      if (resMeals.statusCode == 200) {
        setState(() => _meals = jsonDecode(resMeals.body));
      }
    } catch (e) {
      print("Error: $e");
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _pickDate() async {
    final picked = await showDatePicker(
        context: context,
        initialDate: _selectedDate,
        firstDate: DateTime(2020),
        lastDate: DateTime.now().add(const Duration(days: 1)));
    if (picked != null) {
      setState(() => _selectedDate = picked);
      _refresh();
    }
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> tabs = [
      HomeTab(
          user: _user,
          prog: _prog,
          meals: _meals,
          token: widget.token,
          onRefresh: _refresh,
          selectedDate: _selectedDate),
      LogTab(
          token: widget.token,
          onUpdate: _refresh,
          prog: _prog,
          selectedDate: _selectedDate),
      AITab(token: widget.token, hist: _hist)
    ];
    return Scaffold(
      appBar: AppBar(
          title: InkWell(
              onTap: _pickDate,
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(_user?.name ?? 'Health-ML', style: const TextStyle(fontSize: 16)),
                Text(DateFormat('dd.MM.yyyy').format(_selectedDate),
                    style: const TextStyle(fontSize: 12, color: Colors.tealAccent))
              ])),
          actions: [
            IconButton(icon: const Icon(Icons.calendar_today), onPressed: _pickDate),
            IconButton(icon: const Icon(Icons.refresh), onPressed: _refresh)
          ]),
      body: _loading ? const Center(child: CircularProgressIndicator()) : tabs[_idx],
      bottomNavigationBar: BottomNavigationBar(
          currentIndex: _idx,
          onTap: (i) => setState(() => _idx = i),
          selectedItemColor: Colors.tealAccent,
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Dziś'),
            BottomNavigationBarItem(icon: Icon(Icons.add_circle), label: 'Dodaj'),
            BottomNavigationBarItem(icon: Icon(Icons.insights), label: 'AI')
          ]),
    );
  }
}

class HomeTab extends StatelessWidget {
  final UserData? user;
  final Map<String, dynamic> prog;
  final List meals;
  final String token;
  final VoidCallback onRefresh;
  final DateTime selectedDate;
  const HomeTab(
      {super.key,
      this.user,
      required this.prog,
      required this.meals,
      required this.token,
      required this.onRefresh,
      required this.selectedDate});

  @override
  Widget build(BuildContext context) {
    if (user == null) return const Center(child: CircularProgressIndicator());
    
    // BEZPIECZNE KONWERSJE NUMERYCZNE
    final double kcalIn = (prog['kcal'] as num? ?? 0).toDouble();
    final double protIn = (prog['protein'] as num? ?? 0).toDouble();
    final double carbsIn = (prog['carbs'] as num? ?? 0).toDouble();
    final double fatsIn = (prog['fats'] as num? ?? 0).toDouble();
    final double waterIn = (prog['water'] as num? ?? 0).toDouble();
    final double weightIn = (prog['weight'] as num? ?? 80).toDouble();
    final double waterTarget = user!.waterGoal > 0 ? user!.waterGoal : 2.5;

    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Column(children: [
          Stack(alignment: Alignment.center, children: [
            SizedBox(
                width: 180,
                height: 180,
                child: CircularProgressIndicator(
                    value: (kcalIn / user!.targetKcal).clamp(0, 1),
                    strokeWidth: 12,
                    color: Colors.blueAccent)),
            SizedBox(
                width: 150,
                height: 150,
                child: CircularProgressIndicator(
                    value: (protIn / user!.targetProtein).clamp(0, 1),
                    strokeWidth: 12,
                    color: Colors.orangeAccent)),
            Column(children: [
              Text('${kcalIn.round()}',
                  style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
              Text('z ${user!.targetKcal} kcal',
                  style: const TextStyle(color: Colors.grey, fontSize: 12))
            ])
          ]),
          const SizedBox(height: 24),
          Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            _mini('B', '${protIn.round()}g', Colors.orangeAccent),
            _mini('W', '${carbsIn.round()}g', Colors.greenAccent),
            _mini('T', '${fatsIn.round()}g', Colors.redAccent),
          ]),
          const SizedBox(height: 24),
          Card(
              color: Colors.redAccent.withOpacity(0.1),
              child: ListTile(
                  leading: const Icon(Icons.fitness_center, color: Colors.redAccent),
                  title: const Text('TRENING DNIA',
                      style: TextStyle(
                          fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
                  subtitle: Text(prog['training_log'] ?? "Rest Day",
                      style: const TextStyle(
                          fontSize: 14, fontWeight: FontWeight.bold)))),
          const SizedBox(height: 16),
          Card(
              color: Colors.blueGrey.withOpacity(0.2),
              child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(children: [
                    const Icon(Icons.water_drop, color: Colors.cyanAccent, size: 32),
                    const SizedBox(width: 16),
                    Expanded(
                        child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                          const Text('NAWODNIENIE',
                              style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                  color: Colors.grey)),
                          Text(
                              '${waterIn.toStringAsFixed(1)} / ${waterTarget.toStringAsFixed(1)} L',
                              style: const TextStyle(
                                  fontSize: 18, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          LinearProgressIndicator(
                              value: (waterIn / waterTarget).clamp(0, 1),
                              color: Colors.cyanAccent,
                              backgroundColor: Colors.white10)
                        ])),
                    IconButton(
                        icon: const Icon(Icons.add_circle_outline, color: Colors.cyanAccent),
                        onPressed: () => _showWaterSlider(context, waterIn))
                  ]))),
          const SizedBox(height: 24),
          Align(
              alignment: Alignment.centerLeft,
              child: Text('POSIŁKI (${DateFormat('dd.MM').format(selectedDate)})',
                  style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.grey))),
          const SizedBox(height: 8),
          if (meals.isEmpty)
            const Padding(
                padding: EdgeInsets.all(16),
                child: Text("Brak posiłków dla tej daty.",
                    style: TextStyle(color: Colors.grey))),
          ...meals.map((m) => Card(
                  child: ListTile(
                title: Text(m['name']),
                subtitle: Text(
                    '${m['kcal']} kcal | B:${m['protein']} W:${m['carbs']} T:${m['fats']}'),
                trailing: IconButton(
                    icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
                    onPressed: () async {
                      await http.delete(Uri.parse('$_apiBase/meals/${m['id']}'),
                          headers: {'Authorization': 'Bearer $token'});
                      onRefresh();
                    }),
              )))
        ]),
      ),
    );
  }

  void _showWaterSlider(BuildContext context, double current) {
    double val = 0.25;
    bool addMode = true;
    showDialog(
        context: context,
        builder: (ctx) => StatefulBuilder(
            builder: (context, setST) => AlertDialog(
                    title: const Text('Zmień nawodnienie'),
                    content: Column(mainAxisSize: MainAxisSize.min, children: [
                      Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                        ChoiceChip(
                            label: const Text('DODAJ'),
                            selected: addMode,
                            onSelected: (v) => setST(() => addMode = true),
                            selectedColor: Colors.cyanAccent.withOpacity(0.3)),
                        const SizedBox(width: 8),
                        ChoiceChip(
                            label: const Text('ODEJMIJ'),
                            selected: !addMode,
                            onSelected: (v) => setST(() => addMode = false),
                            selectedColor: Colors.redAccent.withOpacity(0.3))
                      ]),
                      const SizedBox(height: 24),
                      Text('${addMode ? "+" : "-"}${val.toStringAsFixed(2)} L',
                          style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: addMode ? Colors.cyanAccent : Colors.redAccent)),
                      Slider(
                          value: val,
                          min: 0.1,
                          max: 1.5,
                          divisions: 14,
                          label: '${val.toStringAsFixed(2)} L',
                          onChanged: (v) => setST(() => val = v))
                    ]),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Anuluj')),
                      ElevatedButton(
                          onPressed: () async {
                            final dateStr = DateFormat('yyyy-MM-dd').format(selectedDate);
                            double diff = addMode ? val : -val;
                            await http.post(Uri.parse('$_apiBase/progress/'),
                                headers: {
                                  'Content-Type': 'application/json',
                                  'Authorization': 'Bearer $token'
                                },
                                body: jsonEncode({
                                  "date": dateStr,
                                  "weight": prog['weight'] ?? 80.0,
                                  "water": (current + diff).clamp(0, 10),
                                  "kcal": prog['kcal'] ?? 0,
                                  "protein": prog['protein'] ?? 0.0,
                                  "carbs": prog['carbs'] ?? 0.0,
                                  "fats": prog['fats'] ?? 0.0,
                                  "training_log": prog['training_log'] ?? "Rest Day"
                                }));
                            onRefresh();
                            Navigator.pop(ctx);
                          },
                          child: Text(addMode ? 'Dodaj' : 'Odejmij'))
                    ])));
  }

  Widget _mini(String l, String v, Color c) => Column(children: [
        Text(l, style: TextStyle(color: c, fontWeight: FontWeight.bold)),
        Text(v)
      ]);
}

class LogTab extends StatelessWidget {
  final String token;
  final VoidCallback onUpdate;
  final Map<String, dynamic> prog;
  final DateTime selectedDate;
  const LogTab(
      {super.key,
      required this.token,
      required this.onUpdate,
      required this.prog,
      required this.selectedDate});
  @override
  Widget build(BuildContext context) {
    return ListView(padding: const EdgeInsets.all(16), children: [
      _btn(
          context,
          'SZUKAJ JEDZENIA (API)',
          Icons.search,
          Colors.greenAccent,
          () => Navigator.push(
              context,
              MaterialPageRoute(
                  builder: (context) => FoodSearchPage(
                      token: token, selectedDate: selectedDate))).then((_) => onUpdate())),
      _btn(
          context,
          'DODAJ RĘCZNIE',
          Icons.edit_note,
          Colors.orangeAccent,
          () => Navigator.push(
              context,
              MaterialPageRoute(
                  builder: (context) => ManualMealPage(
                      token: token, selectedDate: selectedDate))).then((_) => onUpdate())),
      _btn(
          context,
          'LOGUJ TRENING',
          Icons.fitness_center,
          Colors.redAccent,
          () => Navigator.push(
              context,
              MaterialPageRoute(
                  builder: (context) => WorkoutSelectPage(
                      token: token,
                      prog: prog,
                      selectedDate: selectedDate))).then((_) => onUpdate())),
    ]);
  }

  Widget _btn(BuildContext context, String t, IconData i, Color c, VoidCallback o) =>
      Card(child: ListTile(leading: Icon(i, color: c), title: Text(t), onTap: o));
}

class ManualMealPage extends StatefulWidget {
  final String token;
  final DateTime selectedDate;
  const ManualMealPage({super.key, required this.token, required this.selectedDate});
  @override
  State<ManualMealPage> createState() => _ManualMealPageState();
}

class _ManualMealPageState extends State<ManualMealPage> {
  final _n = TextEditingController(),
      _k = TextEditingController(),
      _p = TextEditingController(),
      _c = TextEditingController(),
      _f = TextEditingController();
  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
            title: Text('Ręczny: ${DateFormat('dd.MM').format(widget.selectedDate)}')),
        body: ListView(padding: const EdgeInsets.all(24), children: [
          TextField(controller: _n, decoration: const InputDecoration(labelText: 'Nazwa')),
          TextField(
              controller: _k,
              decoration: const InputDecoration(labelText: 'Kcal'),
              keyboardType: TextInputType.number),
          TextField(
              controller: _p,
              decoration: const InputDecoration(labelText: 'Białko'),
              keyboardType: TextInputType.number),
          TextField(
              controller: _c,
              decoration: const InputDecoration(labelText: 'Węgle'),
              keyboardType: TextInputType.number),
          TextField(
              controller: _f,
              decoration: const InputDecoration(labelText: 'Tłuszcz'),
              keyboardType: TextInputType.number),
          const SizedBox(height: 32),
          ElevatedButton(
              onPressed: () async {
                await http.post(Uri.parse('$_apiBase/meals/'),
                    headers: {
                      'Content-Type': 'application/json',
                      'Authorization': 'Bearer ${widget.token}'
                    },
                    body: jsonEncode({
                      "date": DateFormat('yyyy-MM-dd').format(widget.selectedDate),
                      "name": _n.text,
                      "kcal": double.parse(_k.text),
                      "protein": double.parse(_p.text),
                      "carbs": double.parse(_c.text),
                      "fats": double.parse(_f.text)
                    }));
                Navigator.pop(context);
              },
              child: const Text('Zapisz'))
        ]));
  }
}

class FoodSearchPage extends StatefulWidget {
  final String token;
  final DateTime selectedDate;
  const FoodSearchPage({super.key, required this.token, required this.selectedDate});
  @override
  State<FoodSearchPage> createState() => _FoodSearchPageState();
}

class _FoodSearchPageState extends State<FoodSearchPage> {
  final _q = TextEditingController();
  List _res = [];
  bool _loading = false;
  Future<void> _search() async {
    if (_q.text.isEmpty) return;
    setState(() => _loading = true);
    try {
      final r = await http
          .get(Uri.parse('$_apiBase/edamam/search?q=${Uri.encodeComponent(_q.text)}'));
      if (r.statusCode == 200) setState(() => _res = jsonDecode(r.body));
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(title: const Text('Szukaj')),
        body: Column(children: [
          Padding(
              padding: const EdgeInsets.all(16),
              child: TextField(
                  controller: _q,
                  decoration: InputDecoration(
                      hintText: "Produkt...",
                      suffixIcon: IconButton(onPressed: _search, icon: const Icon(Icons.search))),
                  onSubmitted: (_) => _search())),
          if (_loading) const LinearProgressIndicator(),
          Expanded(
              child: ListView.builder(
                  itemCount: _res.length,
                  itemBuilder: (c, i) => ListTile(
                      title: Text(_res[i]['label']),
                      subtitle: Text('${_res[i]['kcal']} kcal/100g'),
                      trailing: const Icon(Icons.add),
                      onTap: () async {
                        await http.post(Uri.parse('$_apiBase/meals/'),
                            headers: {
                              'Content-Type': 'application/json',
                              'Authorization': 'Bearer ${widget.token}'
                            },
                            body: jsonEncode({
                              "date": DateFormat('yyyy-MM-dd').format(widget.selectedDate),
                              "name": _res[i]['label'],
                              "kcal": _res[i]['kcal'],
                              "protein": _res[i]['p'],
                              "carbs": _res[i]['c'],
                              "fats": _res[i]['f']
                            }));
                        Navigator.pop(context);
                      })))
        ]));
  }
}

class WorkoutSelectPage extends StatefulWidget {
  final String token;
  final Map<String, dynamic> prog;
  final DateTime selectedDate;
  const WorkoutSelectPage(
      {super.key, required this.token, required this.prog, required this.selectedDate});
  @override
  State<WorkoutSelectPage> createState() => _WorkoutSelectPageState();
}

class _WorkoutSelectPageState extends State<WorkoutSelectPage> {
  Map _exs = {};
  String? _day, _ex;
  final _s = TextEditingController(text: "3"), 
        _r = TextEditingController(text: "10"),
        _w = TextEditingController(text: "0");
  @override
  void initState() {
    super.initState();
    _fetch();
  }

  Future<void> _fetch() async {
    final r = await http.get(Uri.parse('$_apiBase/workouts/exercises'));
    setState(() => _exs = jsonDecode(r.body));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(title: const Text('Trening')),
        body: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(children: [
              DropdownButtonFormField<String>(
                  hint: const Text('Dzień'),
                  value: _day,
                  items: _exs.keys
                      .map((e) => DropdownMenuItem<String>(
                          value: e.toString(), child: Text(e.toString())))
                      .toList(),
                  onChanged: (v) => setState(() {
                        _day = v;
                        _ex = null;
                      })),
              if (_day != null)
                DropdownButtonFormField<String>(
                    hint: const Text('Ćwiczenie'),
                    value: _ex,
                    items: (_exs[_day] as List)
                        .map((e) => DropdownMenuItem<String>(
                            value: e.toString(), child: Text(e.toString())))
                        .toList(),
                    onChanged: (v) => setState(() => _ex = v)),
              const SizedBox(height: 16),
              Row(children: [
                Expanded(
                    child: TextField(
                        controller: _s, 
                        decoration: const InputDecoration(labelText: 'Serie'),
                        keyboardType: TextInputType.number)),
                const SizedBox(width: 16),
                Expanded(
                    child: TextField(
                        controller: _w, 
                        decoration: const InputDecoration(labelText: 'Waga (kg)'),
                        keyboardType: TextInputType.number)),
                const SizedBox(width: 16),
                Expanded(
                    child: TextField(
                        controller: _r,
                        decoration: const InputDecoration(labelText: 'Reps'),
                        keyboardType: TextInputType.number))
              ]),
              const Spacer(),
              ElevatedButton(
                  onPressed: () async {
                    // Format oczekiwany przez ML: Nazwa (SxWkg x R)
                    final logEntry = "$_ex (${_s.text}x${_w.text}kg x ${_r.text})";
                    
                    await http.post(Uri.parse('$_apiBase/progress/'),
                        headers: {
                          'Content-Type': 'application/json',
                          'Authorization': 'Bearer ${widget.token}'
                        },
                        body: jsonEncode({
                          "date": DateFormat('yyyy-MM-dd').format(widget.selectedDate),
                          "weight": (widget.prog['weight'] as num? ?? 80.0).toDouble(),
                          "water": (widget.prog['water'] as num? ?? 0.0).toDouble(),
                          "kcal": (widget.prog['kcal'] as num? ?? 0).toInt(),
                          "protein": (widget.prog['protein'] as num? ?? 0.0).toDouble(),
                          "carbs": (widget.prog['carbs'] as num? ?? 0.0).toDouble(),
                          "fats": (widget.prog['fats'] as num? ?? 0.0).toDouble(),
                          "training_log": logEntry,
                          "sleep_quality": widget.prog['sleep_quality'] ?? 3,
                          "rpe": widget.prog['rpe'] ?? 7
                        }));
                    Navigator.pop(context);
                  },
                  child: const Text('Zapisz'))
            ])));
  }
}

class AITab extends StatefulWidget {
  final String token;
  final List hist;
  const AITab({super.key, required this.token, required this.hist});
  @override
  State<AITab> createState() => _AITabState();
}

class _AITabState extends State<AITab> {
  Map? _ins;
  bool _l = false;
  @override
  void initState() {
    super.initState();
    _fetch();
  }

  Future<void> _fetch() async {
    if (!mounted) return;
    setState(() => _l = true);
    try {
      final r = await http.get(Uri.parse('$_apiBase/ml/insights'),
          headers: {'Authorization': 'Bearer ${widget.token}'});
      if (r.statusCode == 200) setState(() => _ins = jsonDecode(r.body));
    } catch (e) {
      print("AI Error: $e");
    } finally {
      if (mounted) setState(() => _l = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_l) return const Center(child: CircularProgressIndicator());
    if (_ins == null)
      return Center(
          child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        const Text("Brak danych AI."),
        ElevatedButton(onPressed: _fetch, child: const Text("Odśwież"))
      ]));
    
    // BEZPIECZNE TWORZENIE PUNKTÓW WYKRESU
    List<FlSpot> spots = [];
    for (int i = 0; i < widget.hist.length; i++) {
      final w = (widget.hist[i]['weight'] as num? ?? 0.0).toDouble();
      spots.add(FlSpot(i.toDouble(), w));
    }

    return RefreshIndicator(
        onRefresh: _fetch,
        child: ListView(padding: const EdgeInsets.all(24), children: [
          if (_ins!['smart_goal'] != null)
            Card(
                color: Colors.tealAccent.withOpacity(0.1),
                margin: const EdgeInsets.only(bottom: 24),
                child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(children: [
                      const Text('POLECANE NA DZIŚ (AI)',
                          style: TextStyle(
                              fontSize: 12, fontWeight: FontWeight.bold, color: Colors.tealAccent)),
                      const SizedBox(height: 12),
                      Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
                        _goalMetric('Kalorie', '${_ins!['smart_goal']['target_kcal']}', 'kcal'),
                        _goalMetric('Białko', '${_ins!['smart_goal']['target_p']}', 'g'),
                        _goalMetric('Woda', '${_ins!['smart_goal']['water']}', 'L'),
                      ]),
                      if (_ins!['recommendation'] != null) ...[
                        const Divider(height: 32),
                        Text(_ins!['recommendation']['msg'] ?? "",
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontStyle: FontStyle.italic, fontSize: 13))
                      ]
                    ]))),
          const Text('Trend Wagi', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          SizedBox(
              height: 150,
              child: LineChart(LineChartData(
                  gridData: const FlGridData(show: false),
                  titlesData: const FlTitlesData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                        spots: spots.isNotEmpty ? spots : [const FlSpot(0, 0)],
                        isCurved: true,
                        color: Colors.tealAccent)
                  ]))),
          const SizedBox(height: 24),
          _aiCard(Icons.auto_graph, 'Analiza Plateau', _ins!['plateau']['msg'] ?? "Brak danych"),
          _aiCard(Icons.tips_and_updates, 'AI Sugestia', _ins!['recommendation']['msg'] ?? "Zbieranie danych..."),
          _aiCard(Icons.fitness_center, 'Postępy Treningowe', _ins!['training']['trend'] ?? "Brak treningów")
        ]));
  }

  Widget _goalMetric(String l, String v, String u) => Column(children: [
        Text(l, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        Text(v, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        Text(u, style: const TextStyle(color: Colors.grey, fontSize: 10)),
      ]);

  Widget _aiCard(IconData i, String t, String s) => Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
          leading: Icon(i, color: Colors.tealAccent),
          title: Text(t, style: const TextStyle(fontSize: 12, color: Colors.grey)),
          subtitle: Text(s, style: const TextStyle(fontWeight: FontWeight.bold))));
}

class SettingsPage extends StatefulWidget {
  final String token;
  final UserData? user;
  const SettingsPage({super.key, required this.token, this.user});
  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  late TextEditingController _k, _p, _w;
  @override
  void initState() {
    super.initState();
    _k = TextEditingController(text: widget.user?.targetKcal.toString());
    _p = TextEditingController(text: widget.user?.targetProtein.toString());
    _w = TextEditingController(text: widget.user?.waterGoal.toString());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(title: const Text('Cele')),
        body: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(children: [
              TextField(controller: _k, decoration: const InputDecoration(labelText: 'Kcal')),
              TextField(controller: _p, decoration: const InputDecoration(labelText: 'Białko')),
              TextField(controller: _w, decoration: const InputDecoration(labelText: 'Woda')),
              const SizedBox(height: 32),
              ElevatedButton(
                  onPressed: () async {
                    await http.post(Uri.parse('$_apiBase/users/goals'),
                        headers: {
                          'Content-Type': 'application/json',
                          'Authorization': 'Bearer ${widget.token}'
                        },
                        body: jsonEncode({
                          "target_kcal": int.parse(_k.text),
                          "target_protein": double.parse(_p.text),
                          "water_goal": double.parse(_w.text)
                        }));
                    Navigator.pop(context);
                  },
                  child: const Text('Zapisz'))
            ])));
  }
}
