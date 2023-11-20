import "package:aw40_hub_frontend/main.dart";
import "package:aw40_hub_frontend/providers/providers.dart";
import "package:aw40_hub_frontend/routing/router.dart";
import "package:aw40_hub_frontend/services/services.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:http/http.dart" as http;
import "package:provider/provider.dart";
import "package:routemaster/routemaster.dart";

class AWHubApp extends StatelessWidget {
  const AWHubApp({super.key});

  @override
  Widget build(final BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<AuthProvider>(
          create: (_) => AuthProvider(
            http.Client(),
            StorageService(),
            TokenService(),
            AuthService(),
            ConfigService(),
          ),
        ),
        ChangeNotifierProvider<CaseProvider>(
          create: (_) => CaseProvider(HttpService()),
        ),
        ChangeNotifierProvider<DiagnosisProvider>(
          create: (_) => DiagnosisProvider(HttpService()),
        )
      ],
      child: MaterialApp.router(
        title: "AW 4.0 Hub",
        localizationsDelegates: context.localizationDelegates,
        supportedLocales: context.supportedLocales,
        locale: context.locale,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: kPrimaryColor,
            brightness: Brightness.dark,
            secondary: kSecondaryColor,
          ),
          useMaterial3: true,
        ),
        routerDelegate: RoutemasterDelegate(
          routesBuilder: (BuildContext context) {
            final authProvider = Provider.of<AuthProvider>(context);
            return getRouteMap(authProvider);
          },
          navigatorKey: globalNavKey,
        ),
        routeInformationParser: const RoutemasterParser(),
      ),
    );
  }
}
