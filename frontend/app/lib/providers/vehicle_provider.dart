import "dart:convert";

import "package:aw40_hub_frontend/dtos/vehicle_dto.dart";
import "package:aw40_hub_frontend/exceptions/app_exception.dart";
import "package:aw40_hub_frontend/models/vehicle_model.dart";
import "package:aw40_hub_frontend/providers/auth_provider.dart";
import "package:aw40_hub_frontend/services/helper_service.dart";
import "package:aw40_hub_frontend/services/http_service.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:flutter/foundation.dart";
import "package:http/http.dart";
import "package:logging/logging.dart";

class VehicleProvider with ChangeNotifier {
  VehicleProvider(this._httpService);

  final HttpService _httpService;

  final Logger _logger = Logger("vehicle_provider");
  late final String workshopId;

  String? _authToken;

  Future<List<VehicleModel>> getSharedVehicles() async {
    final String authToken = _getAuthToken();
    final Response response = await _httpService.getSharedVehicles(
      authToken,
    );
    if (response.statusCode != 200) {
      _logger.warning(
        "Could not get diagnoses. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return [];
    }
    final json = jsonDecode(response.body);
    if (json is! List) {
      _logger.warning("Could not decode json response to List.");
      return [];
    }
    return json.map((e) => VehicleDto.fromJson(e).toModel()).toList();
  }

  Future<void> fetchAndSetAuthToken(AuthProvider authProvider) async {
    _authToken = await authProvider.getAuthToken();
  }

  String _getAuthToken() {
    final String? authToken = _authToken;
    if (authToken == null) {
      throw AppException(
        exceptionMessage: "Called CaseProvider without auth token.",
        exceptionType: ExceptionType.unexpectedNullValue,
      );
    }
    return authToken;
  }
}
