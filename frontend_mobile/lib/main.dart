import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform, File;
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:image_picker/image_picker.dart';

void main() { runApp(const HealthMLApp()); }

class HealthMLApp extends StatelessWidget {
  const HealthMLApp({super.key});
  @override Widget build(BuildContext context) {
    return MaterialApp(title: 'Health-ML Optimizer', debugShowCheckedModeBanner: false,
      theme: ThemeData(brightness: Brightness.dark, scaffoldBackgroundColor: const Color(0xFF0F0F0F), colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal, brightness: Brightness.dark, primary: Colors.tealAccent), useMaterial3: true),
      home: const LoginPage(),
    );
  }
}

// --- UTILS ---
String get _apiBase {
  if (kIsWeb) return 'http://localhost:8000';
  try { if (Platform.isAndroid) return 'http://10.0.2.2:8000'; } catch (_) {}
  return 'http://localhost:8000';
}

class UserData {
  final int id; final String name, email, goal; final int targetKcal; final double targetProtein, waterGoal;
  UserData({required this.id, required this.name, required this.email, required this.goal, required this.targetKcal, required this.targetProtein, required this.waterGoal});
  factory UserData.fromJson(Map<String, dynamic> json) {
    return UserData(id: json['id'], name: json['name'], email: json['email'], goal: json['goal'], targetKcal: json['target_kcal'], targetProtein: json['target_protein'].toDouble(), waterGoal: json['water_goal'].toDouble());
  }
}

// --- PAGES ---
class LoginPage extends StatefulWidget { const LoginPage({super.key}); @override State<LoginPage> createState() => _LoginPageState(); }
class _LoginPageState extends State<LoginPage> {
  final _e = TextEditingController(), _p = TextEditingController(); bool _l = false;
  Future<void> _login() async {
    setState(() => _l = true);
    try {
      final res = await http.post(Uri.parse('$_apiBase/auth/token'), body: {'username': _e.text, 'password': _p.text});
      if (res.statusCode == 200) { Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => DashboardContainer(token: json.decode(res.body)['access_token']))); }
      else { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Błąd logowania'))); }
    } finally { setState(() => _l = false); }
  }
  @override Widget build(BuildContext context) {
    return Scaffold(body: Center(child: SingleChildScrollView(padding: const EdgeInsets.all(32), child: Column(children: [
      const Icon(Icons.bolt, size: 80, color: Colors.tealAccent), const Text('Health-ML', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)), const SizedBox(height: 48),
      TextField(controller: _e, decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder())), const SizedBox(height: 16),
      TextField(controller: _p, decoration: const InputDecoration(labelText: 'Hasło', border: OutlineInputBorder()), obscureText: true, onSubmitted: (_) => _login()), const SizedBox(height: 32),
      _l ? const CircularProgressIndicator() : SizedBox(width: double.infinity, height: 50, child: ElevatedButton(onPressed: _login, child: const Text('Zaloguj się'))),
      TextButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const RegisterPage())), child: const Text('Zarejestruj się'))
    ]))));
  }
}

class RegisterPage extends StatefulWidget { const RegisterPage({super.key}); @override State<RegisterPage> createState() => _RegisterPageState(); }
class _RegisterPageState extends State<RegisterPage> {
  final _n = TextEditingController(), _e = TextEditingController(), _p = TextEditingController(), _w = TextEditingController(text: "80");
  String _g = "Mężczyzna", _goal = "utrzymanie";
  @override Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('Nowy Profil')), body: ListView(padding: const EdgeInsets.all(24), children: [
      TextField(controller: _n, decoration: const InputDecoration(labelText: 'Imię')), TextField(controller: _e, decoration: const InputDecoration(labelText: 'Email')),
      TextField(controller: _p, decoration: const InputDecoration(labelText: 'Hasło'), obscureText: true), TextField(controller: _w, decoration: const InputDecoration(labelText: 'Waga (kg)')),
      DropdownButtonFormField<String>(value: _g, items: ["Mężczyzna", "Kobieta"].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(), onChanged: (v) => setState(() => _g = v!), decoration: const InputDecoration(labelText: 'Płeć')),
      DropdownButtonFormField<String>(value: _goal, items: ["redukcja", "utrzymanie", "masa"].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(), onChanged: (v) => setState(() => _goal = v!), decoration: const InputDecoration(labelText: 'Cel')),
      const SizedBox(height: 32), ElevatedButton(onPressed: () async {
        await http.post(Uri.parse('$_apiBase/auth/register'), headers: {'Content-Type': 'application/json'}, body: jsonEncode({"name": _n.text, "email": _e.text, "password": _p.text, "age": 25, "height": 180, "weight": double.parse(_w.text), "gender": _g, "activity": 1.55, "goal": _goal}));
        Navigator.pop(context);
      }, child: const Text('Stwórz'))
    ]));
  }
}

// --- CONTAINER ---
class DashboardContainer extends StatefulWidget {
  final String token; const DashboardContainer({super.key, required this.token});
  @override State<DashboardContainer> createState() => _DashboardContainerState();
}
class _DashboardContainerState extends State<DashboardContainer> {
  int _idx = 0; UserData? _user; Map<String, dynamic> _prog = {"kcal": 0, "protein": 0.0, "carbs": 0.0, "fats": 0.0, "water": 0.0, "weight": 80.0}; List _meals = []; List _hist = [];
  @override void initState() { super.initState(); _refresh(); }
  Future<void> _refresh() async {
    final auth = {'Authorization': 'Bearer ${widget.token}'};
    final resMe = await http.get(Uri.parse('$_apiBase/users/me'), headers: auth);
    if (resMe.statusCode == 200) setState(() => _user = UserData.fromJson(jsonDecode(resMe.body)));
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
    final resProg = await http.get(Uri.parse('$_apiBase/progress/'), headers: auth);
    if (resProg.statusCode == 200) {
      final List l = jsonDecode(resProg.body); _hist = l;
      final t = l.firstWhere((x) => x['date'] == today, orElse: () => null);
      if (t != null) setState(() => _prog = t);
    }
    final resMeals = await http.get(Uri.parse('$_apiBase/meals/$today'), headers: auth);
    if (resMeals.statusCode == 200) setState(() => _meals = jsonDecode(resMeals.body));
  }
  @override Widget build(BuildContext context) {
    final List<Widget> tabs = [
      HomeTab(user: _user, prog: _prog, meals: _meals, token: widget.token, onRefresh: _refresh),
      LogTab(token: widget.token, onUpdate: _refresh, prog: _prog),
      AITab(token: widget.token, hist: _hist)
    ];
    return Scaffold(
      appBar: AppBar(title: Text(_user != null ? 'Cześć, ${_user!.name}' : 'Health-ML'), actions: [IconButton(icon: const Icon(Icons.settings), onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => SettingsPage(token: widget.token, user: _user))).then((_) => _refresh()))]),
      body: _user == null ? const Center(child: CircularProgressIndicator()) : tabs[_idx],
      bottomNavigationBar: BottomNavigationBar(currentIndex: _idx, onTap: (i) => setState(() => _idx = i), selectedItemColor: Colors.tealAccent, items: const [BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Dziś'), BottomNavigationBarItem(icon: Icon(Icons.add_circle), label: 'Dodaj'), BottomNavigationBarItem(icon: Icon(Icons.insights), label: 'AI')]),
    );
  }
}

// --- HOME ---
class HomeTab extends StatelessWidget {
  final UserData? user; final Map<String, dynamic> prog; final List meals; final String token; final VoidCallback onRefresh;
  const HomeTab({super.key, this.user, required this.prog, required this.meals, required this.token, required this.onRefresh});

  @override Widget build(BuildContext context) {
    if (user == null) return const SizedBox();
    double waterVal = (prog['water'] ?? 0.0).toDouble();
    double waterTarget = user!.waterGoal > 0 ? user!.waterGoal : 2.5;

    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24), 
        child: Column(children: [
          Stack(alignment: Alignment.center, children: [
            SizedBox(width: 180, height: 180, child: CircularProgressIndicator(value: (prog['kcal']/user!.targetKcal).clamp(0,1), strokeWidth: 12, color: Colors.blueAccent)),
            SizedBox(width: 150, height: 150, child: CircularProgressIndicator(value: (prog['protein']/user!.targetProtein).clamp(0,1), strokeWidth: 12, color: Colors.orangeAccent)),
            Column(children: [Text('${prog['kcal']}', style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)), const Text('kcal', style: TextStyle(color: Colors.grey))])
          ]),
          const SizedBox(height: 24),
          Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            _mini('B', '${prog['protein'].round()}g', Colors.orangeAccent), _mini('W', '${prog['carbs'].round()}g', Colors.greenAccent), _mini('T', '${prog['fats'].round()}g', Colors.redAccent),
          ]),
          const SizedBox(height: 32),
          
          // SEKKO WODY
          Card(
            color: Colors.blueGrey.withOpacity(0.2),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(children: [
                const Icon(Icons.water_drop, color: Colors.cyanAccent, size: 32),
                const SizedBox(width: 16),
                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  const Text('NAWODNIENIE', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey)),
                  Text('${waterVal.toStringAsFixed(1)} / ${waterTarget.toStringAsFixed(1)} L', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  LinearProgressIndicator(value: (waterVal / waterTarget).clamp(0, 1), color: Colors.cyanAccent, backgroundColor: Colors.white10),
                ])),
                IconButton(
                  icon: const Icon(Icons.add_circle_outline, color: Colors.cyanAccent),
                  onPressed: () => _showWaterSlider(context, waterVal),
                )
              ]),
            ),
          ),
          
          const SizedBox(height: 32),
          const Align(alignment: Alignment.centerLeft, child: Text('DZISIEJSZE POSIŁKI', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey))),
          const SizedBox(height: 8),
          ... meals.map((m) => Card(child: ListTile(
            title: Text(m['name']), subtitle: Text('${m['kcal']} kcal | B:${m['protein']} W:${m['carbs']} T:${m['fats']}'),
            trailing: IconButton(icon: const Icon(Icons.delete_outline, color: Colors.redAccent), onPressed: () async {
              await http.delete(Uri.parse('$_apiBase/meals/${m['id']}'), headers: {'Authorization': 'Bearer $token'}); onRefresh();
            }),
          ))),
        ]),
      ),
    );
  }

  void _showWaterSlider(BuildContext context, double current) {
    double val = 0.25; bool addMode = true;
    showDialog(context: context, builder: (ctx) => StatefulBuilder(builder: (context, setST) => AlertDialog(
      title: const Text('Zmień nawodnienie'),
      content: Column(mainAxisSize: MainAxisSize.min, children: [
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          ChoiceChip(label: const Text('DODAJ'), selected: addMode, onSelected: (v) => setST(() => addMode = true), selectedColor: Colors.cyanAccent.withOpacity(0.3)),
          const SizedBox(width: 8),
          ChoiceChip(label: const Text('ODEJMIJ'), selected: !addMode, onSelected: (v) => setST(() => addMode = false), selectedColor: Colors.redAccent.withOpacity(0.3)),
        ]),
        const SizedBox(height: 24),
        Text('${addMode ? "+" : "-"}${val.toStringAsFixed(2)} L', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: addMode ? Colors.cyanAccent : Colors.redAccent)),
        Slider(value: val, min: 0.1, max: 1.5, divisions: 14, label: '${val.toStringAsFixed(2)} L', onChanged: (v) => setST(() => val = v)),
      ]),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Anuluj')),
        ElevatedButton(onPressed: () async {
          final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
          double diff = addMode ? val : -val;
          await http.post(Uri.parse('$_apiBase/progress/'), 
            headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'}, 
            body: jsonEncode({
              "date": today, "weight": prog['weight'] ?? 80.0, "water": (current + diff).clamp(0, 10), 
              "kcal": prog['kcal'] ?? 0, "protein": prog['protein'] ?? 0.0, "carbs": prog['carbs'] ?? 0.0, "fats": prog['fats'] ?? 0.0
            }));
          onRefresh(); Navigator.pop(ctx);
        }, child: Text(addMode ? 'Dodaj' : 'Odejmij'))
      ],
    )));
  }
  Widget _mini(String l, String v, Color c) => Column(children: [Text(l, style: TextStyle(color: c, fontWeight: FontWeight.bold)), Text(v)]);
}

// --- LOG ---
class LogTab extends StatelessWidget {
  final String token; final VoidCallback onUpdate; final Map<String, dynamic> prog;
  const LogTab({super.key, required this.token, required this.onUpdate, required this.prog});
  @override Widget build(BuildContext context) {
    return ListView(padding: const EdgeInsets.all(16), children: [
      _btn(context, 'SZUKAJ JEDZENIA (API)', Icons.search, Colors.greenAccent, () => Navigator.push(context, MaterialPageRoute(builder: (context) => FoodSearchPage(token: token))).then((_) => onUpdate())),
      _btn(context, 'DODAJ RĘCZNIE', Icons.edit_note, Colors.orangeAccent, () => Navigator.push(context, MaterialPageRoute(builder: (context) => ManualMealPage(token: token))).then((_) => onUpdate())),
      _btn(context, 'LOGUJ TRENING', Icons.fitness_center, Colors.redAccent, () => Navigator.push(context, MaterialPageRoute(builder: (context) => WorkoutSelectPage(token: token, prog: prog))).then((_) => onUpdate())),
    ]);
  }
  Widget _btn(BuildContext context, String t, IconData i, Color c, VoidCallback o) => Card(child: ListTile(leading: Icon(i, color: c), title: Text(t), onTap: o));
}

// --- MANUAL MEAL ---
class ManualMealPage extends StatefulWidget {
  final String token; const ManualMealPage({super.key, required this.token});
  @override State<ManualMealPage> createState() => _ManualMealPageState();
}
class _ManualMealPageState extends State<ManualMealPage> {
  final _n = TextEditingController(), _k = TextEditingController(), _p = TextEditingController(), _c = TextEditingController(), _f = TextEditingController();
  @override Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('Ręczny wpis')), body: ListView(padding: const EdgeInsets.all(24), children: [
      TextField(controller: _n, decoration: const InputDecoration(labelText: 'Nazwa posiłku')),
      TextField(controller: _k, decoration: const InputDecoration(labelText: 'Kcal'), keyboardType: TextInputType.number),
      TextField(controller: _p, decoration: const InputDecoration(labelText: 'Białko (g)'), keyboardType: TextInputType.number),
      TextField(controller: _c, decoration: const InputDecoration(labelText: 'Węglowodany (g)'), keyboardType: TextInputType.number),
      TextField(controller: _f, decoration: const InputDecoration(labelText: 'Tłuszcz (g)'), keyboardType: TextInputType.number),
      const SizedBox(height: 32),
      ElevatedButton(onPressed: () async {
        await http.post(Uri.parse('$_apiBase/meals/'), headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ${widget.token}'},
          body: jsonEncode({"date": DateFormat('yyyy-MM-dd').format(DateTime.now()), "name": _n.text, "kcal": double.parse(_k.text), "protein": double.parse(_p.text), "carbs": double.parse(_c.text), "fats": double.parse(_f.text)}));
        Navigator.pop(context);
      }, child: const Text('Zapisz posiłek'))
    ]));
  }
}

// --- FOOD SEARCH ---
class FoodSearchPage extends StatefulWidget {
  final String token; const FoodSearchPage({super.key, required this.token});
  @override State<FoodSearchPage> createState() => _FoodSearchPageState();
}
class _FoodSearchPageState extends State<FoodSearchPage> {
  final _q = TextEditingController(); List _res = []; bool _loading = false;
  Future<void> _search() async {
    if (_q.text.isEmpty) return;
    setState(() => _loading = true);
    try {
      final r = await http.get(Uri.parse('$_apiBase/edamam/search?q=${Uri.encodeComponent(_q.text)}'));
      if (r.statusCode == 200) {
        setState(() => _res = jsonDecode(r.body));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Błąd API: ${r.statusCode}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Błąd połączenia: $e')));
    } finally { setState(() => _loading = false); }
  }
  void _add(Map f) {
    final qty = TextEditingController(text: "100");
    showDialog(context: context, builder: (ctx) => StatefulBuilder(builder: (context, setST) {
      double factor = (double.tryParse(qty.text) ?? 0) / 100;
      return AlertDialog(
        title: Text(f['label']), 
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(
            controller: qty, 
            decoration: const InputDecoration(labelText: 'Ilość (g)'), 
            keyboardType: TextInputType.number,
            onChanged: (v) => setST(() {}),
          ),
          const SizedBox(height: 16),
          if (factor > 0) Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            _mLabel('Kcal', (f['kcal'] * factor).round().toString()),
            _mLabel('B', (f['p'] * factor).toStringAsFixed(1)),
            _mLabel('W', (f['c'] * factor).toStringAsFixed(1)),
            _mLabel('T', (f['f'] * factor).toStringAsFixed(1)),
          ]),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Anuluj')),
          ElevatedButton(onPressed: () async {
            double factor = (double.tryParse(qty.text) ?? 100) / 100;
            await http.post(Uri.parse('$_apiBase/meals/'), headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ${widget.token}'},
              body: jsonEncode({"date": DateFormat('yyyy-MM-dd').format(DateTime.now()), "name": f['label'], "kcal": f['kcal']*factor, "protein": f['p']*factor, "carbs": f['c']*factor, "fats": f['f']*factor}));
            Navigator.pop(ctx); Navigator.pop(context);
          }, child: const Text('Dodaj'))
        ],
      );
    }));
  }
  Widget _mLabel(String l, String v) => Column(children: [Text(l, style: const TextStyle(fontSize: 10, color: Colors.grey)), Text(v, style: const TextStyle(fontWeight: FontWeight.bold))]);
  @override Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('Edamam API')), body: Column(children: [
      Padding(padding: const EdgeInsets.all(16), child: TextField(controller: _q, decoration: InputDecoration(hintText: "Szukaj...", suffixIcon: IconButton(onPressed: _search, icon: const Icon(Icons.search))), onSubmitted: (_) => _search())),
      if (_loading) const LinearProgressIndicator(),
      Expanded(child: ListView.builder(itemCount: _res.length, itemBuilder: (c, i) => ListTile(title: Text(_res[i]['label']), subtitle: Text('${_res[i]['kcal']} kcal/100g'), trailing: const Icon(Icons.add), onTap: () => _add(_res[i]))))
    ]));
  }
}

// --- WORKOUT SELECT ---
class WorkoutSelectPage extends StatefulWidget {
  final String token; final Map<String, dynamic> prog; const WorkoutSelectPage({super.key, required this.token, required this.prog});
  @override State<WorkoutSelectPage> createState() => _WorkoutSelectPageState();
}
class _WorkoutSelectPageState extends State<WorkoutSelectPage> {
  Map _exs = {}; String? _day, _ex; final _s = TextEditingController(text: "3"), _r = TextEditingController(text: "10");
  @override void initState() { super.initState(); _fetch(); }
  Future<void> _fetch() async { final r = await http.get(Uri.parse('$_apiBase/workouts/exercises')); setState(() => _exs = jsonDecode(r.body)); }
  @override Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('Trening')), body: Padding(padding: const EdgeInsets.all(24), child: Column(children: [
      DropdownButtonFormField<String>(hint: const Text('Dzień'), value: _day, items: _exs.keys.map((e) => DropdownMenuItem<String>(value: e.toString(), child: Text(e.toString()))).toList(), onChanged: (v) => setState(() { _day = v; _ex = null; })),
      if (_day != null) DropdownButtonFormField<String>(hint: const Text('Ćwiczenie'), value: _ex, items: (_exs[_day] as List).map((e) => DropdownMenuItem<String>(value: e.toString(), child: Text(e.toString()))).toList(), onChanged: (v) => setState(() => _ex = v)),
      Row(children: [Expanded(child: TextField(controller: _s, decoration: const InputDecoration(labelText: 'Serie'))), const SizedBox(width: 16), Expanded(child: TextField(controller: _r, decoration: const InputDecoration(labelText: 'Powtórzenia')))]),
      const Spacer(), ElevatedButton(onPressed: () async {
        await http.post(Uri.parse('$_apiBase/progress/'), headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ${widget.token}'}, body: jsonEncode({"date": DateFormat('yyyy-MM-dd').format(DateTime.now()), "weight": widget.prog['weight'], "water": widget.prog['water'], "kcal": widget.prog['kcal'], "protein": widget.prog['protein'], "carbs": widget.prog['carbs'], "fats": widget.prog['fats'], "training_log": "$_ex (${_s.text}x${_r.text})", "sleep_quality": 3, "rpe": 7}));
        Navigator.pop(context);
      }, child: const Text('Zapisz'))
    ])));
  }
}

// --- AI TAB ---
class AITab extends StatefulWidget {
  final String token; final List hist; const AITab({super.key, required this.token, required this.hist});
  @override State<AITab> createState() => _AITabState();
}
class _AITabState extends State<AITab> {
  Map? _ins; @override void initState() { super.initState(); _fetch(); }
  Future<void> _fetch() async { final r = await http.get(Uri.parse('$_apiBase/ml/insights'), headers: {'Authorization': 'Bearer ${widget.token}'}); setState(() => _ins = jsonDecode(r.body)); }
  @override Widget build(BuildContext context) {
    if (_ins == null) return const Center(child: CircularProgressIndicator());
    List<FlSpot> spots = []; for (int i = 0; i < widget.hist.length; i++) spots.add(FlSpot(i.toDouble(), widget.hist[i]['weight'].toDouble()));
    return ListView(padding: const EdgeInsets.all(24), children: [
      const Text('Trend Wagi', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)), const SizedBox(height: 16),
      SizedBox(height: 150, child: LineChart(LineChartData(gridData: const FlGridData(show: false), titlesData: const FlTitlesData(show: false), lineBarsData: [LineChartBarData(spots: spots.isNotEmpty ? spots : [const FlSpot(0,0)], isCurved: true, color: Colors.tealAccent)]))),
      ListTile(leading: const Icon(Icons.auto_graph), title: const Text('Plateau'), subtitle: Text(_ins!['plateau']['msg'])),
      ListTile(leading: const Icon(Icons.tips_and_updates), title: const Text('AI mówi'), subtitle: Text(_ins!['recommendation']['msg'])),
    ]);
  }
}

// --- SETTINGS ---
class SettingsPage extends StatefulWidget {
  final String token; final UserData? user; const SettingsPage({super.key, required this.token, this.user});
  @override State<SettingsPage> createState() => _SettingsPageState();
}
class _SettingsPageState extends State<SettingsPage> {
  late TextEditingController _k, _p, _w;
  @override void initState() { super.initState(); _k = TextEditingController(text: widget.user?.targetKcal.toString()); _p = TextEditingController(text: widget.user?.targetProtein.toString()); _w = TextEditingController(text: widget.user?.waterGoal.toString()); }
  @override Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('Cele')), body: Padding(padding: const EdgeInsets.all(24), child: Column(children: [
      TextField(controller: _k, decoration: const InputDecoration(labelText: 'Kcal')), TextField(controller: _p, decoration: const InputDecoration(labelText: 'Białko (g)')),
      TextField(controller: _w, decoration: const InputDecoration(labelText: 'Woda (L)')),
      const SizedBox(height: 32), ElevatedButton(onPressed: () async {
        await http.post(Uri.parse('$_apiBase/users/goals'), headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ${widget.token}'}, body: jsonEncode({"target_kcal": int.parse(_k.text), "target_protein": double.parse(_p.text), "water_goal": double.parse(_w.text)}));
        Navigator.pop(context);
      }, child: const Text('Zapisz'))
    ])));
  }
}
