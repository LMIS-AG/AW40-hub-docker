import "package:aw40_hub_frontend/providers/providers.dart";
import "package:aw40_hub_frontend/scaffolds/scaffolds.dart";
import "package:aw40_hub_frontend/screens/diagnosis_screen.dart";
import "package:aw40_hub_frontend/screens/screens.dart";
import "package:aw40_hub_frontend/utils/constants.dart";
import "package:flutter/foundation.dart";
import "package:flutter/material.dart";
import "package:logging/logging.dart";
import "package:routemaster/routemaster.dart";
import "package:universal_html/html.dart";

RouteMap getRouteMap(AuthProvider authProvider) {
  final Logger logger = Logger("get_route_map");

  final Map<String, PageBuilder> routes = {};
  RouteSettings Function(String path) onUnknownRoute;

  final bool isLoggedIn = authProvider.isLoggedIn();
  logger.info("isLoggedIn: $isLoggedIn");
  if (!isLoggedIn) {
    onUnknownRoute = (String route) {
      logger.info(
        "Requested route $route, user not logged in, returning LoginScreen.",
      );
      final String? currentBrowserUrl = kIsWeb ? window.location.href : null;
      return MaterialPage<Widget>(
        child: LoginScreen(currentBrowserUrl: currentBrowserUrl),
      );
    };
  } else {
    routes.addAll(_basicRoutes);
    onUnknownRoute = (String route) {
      return const MaterialPage<Widget>(
        child: ScaffoldWrapper(
          currentIndex: -1, // No nav item selected.
          child: PageNotFoundScreen(),
        ),
      );
    };
  }

  final RouteMap routeMap = RouteMap(
    routes: routes,
    onUnknownRoute: onUnknownRoute,
  );
  return routeMap;
}

Map<String, PageBuilder> _basicRoutes = {
  "/": (RouteData info) {
    return const Redirect(kRouteDiagnosis);
  },
  kRouteDiagnosisDetails: (RouteData info) {
    return const MaterialPage<Widget>(
      child: ScaffoldWrapper(
        child: DiagnosisScreen(),
      ),
    );
  },
  kRouteDiagnosis: (RouteData info) {
    return const MaterialPage<Widget>(
      child: ScaffoldWrapper(
        child: DiagnosisScreen(),
      ),
    );
  },
  kRouteCases: (RouteData info) {
    return const MaterialPage<Widget>(
      child: ScaffoldWrapper(
        child: CasesScreen(),
      ),
    );
  },
  kRouteCustomers: (RouteData info) {
    return const MaterialPage<Widget>(
      child: ScaffoldWrapper(
        child: CustomersScreen(),
      ),
    );
  },
  kRouteVecicles: (RouteData info) {
    return const MaterialPage<Widget>(
      child: ScaffoldWrapper(
        child: VehiclesScreen(),
      ),
    );
  },
};
