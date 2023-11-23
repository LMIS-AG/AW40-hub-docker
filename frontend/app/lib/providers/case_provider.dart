import "dart:convert";

import "package:aw40_hub_frontend/dtos/dtos.dart";
import "package:aw40_hub_frontend/models/models.dart";
import "package:aw40_hub_frontend/services/services.dart";
import "package:flutter/material.dart";
import "package:http/http.dart";
import "package:logging/logging.dart";

class CaseProvider with ChangeNotifier {
  CaseProvider(this._httpService);
  final HttpService _httpService;

  final Logger _logger = Logger("case_provider");
  late String workShopId;
  bool _showSharedCases = true;
  bool get showSharedCases => _showSharedCases;
  List<CaseModel> _cases = [];
  int? lastModifiedCaseIndex;

  void resetCases() {
    _cases = [];
  }

  Future<void> toggleShowSharedCases() async {
    _showSharedCases = !_showSharedCases;
    await _loadCurrentCases();
    notifyListeners();
  }

  /// Returns [_cases]. If empty, will attempt to fetch data before returning.
  Future<List<CaseModel>> getCurrentCases() async {
    // * In the rare case that there are no cases, this will result in a
    // * redundant call to _loadCurrentCases()..
    if (_cases.isEmpty) await _loadCurrentCases();
    return _cases;
  }

  /// Depending on [_showSharedCases], call [_httpService.getCases()] or
  /// [_httpService.getSharedCases()].
  Future<bool> _loadCurrentCases() async {
    // * Return value currently not used.
    final Response response;
    if (_showSharedCases) {
      response = await _httpService.getSharedCases();
    } else {
      response = await _httpService.getCases(workShopId);
    }
    if (response.statusCode != 200) {
      _logger.warning(
        "Could not get ${_showSharedCases ? 'shared ' : ''}cases. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return false;
    }
    _cases = _jsonBodyToCaseModelList(response.body);
    return true;
  }

  List<CaseModel> _jsonBodyToCaseModelList(String jsonBody) {
    final List<dynamic> dynamicList = jsonDecode(jsonBody);
    final List<CaseModel> caseModels = [];
    for (final caseJson in dynamicList) {
      final CaseDto caseDto = CaseDto.fromJson(caseJson);
      final CaseModel caseModel = caseDto.toModel();
      caseModels.add(caseModel);
    }
    return caseModels;
  }

  Future<bool> addCase(NewCaseDto newCaseDto) async {
    final Map<String, dynamic> newCaseJson = newCaseDto.toJson();
    final Response response =
        await _httpService.addCase(workShopId, newCaseJson);
    if (response.statusCode != 201) {
      _logger.warning(
        "Could not add case. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return false;
    }
    final Map<String, dynamic> body = jsonDecode(response.body);
    final CaseDto receivedCase = CaseDto.fromJson(body);
    _cases.add(receivedCase.toModel());
    notifyListeners();
    return true;
  }

  Future<bool> updateCase(String caseId, CaseUpdateDto updateCaseDto) async {
    final Map<String, dynamic> updateCaseJson = updateCaseDto.toJson();
    final Response response =
        await _httpService.updateCase(workShopId, caseId, updateCaseJson);
    if (response.statusCode != 200) {
      _logger.warning(
        "Could not update case. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return false;
    }
    final Map<String, dynamic> body = jsonDecode(response.body);
    final CaseDto receivedCase = CaseDto.fromJson(body);

    final CaseModel caseModelToReplace =
        _cases.firstWhere((caseModel) => caseModel.id == caseId);
    final int index = _cases.indexOf(caseModelToReplace);
    lastModifiedCaseIndex = index;
    _cases[index] = receivedCase.toModel();

    notifyListeners();
    return true;
  }

  Future<bool> deleteCase(String caseId) async {
    final Response response = await _httpService.deleteCase(workShopId, caseId);
    if (response.statusCode != 200) {
      _logger.warning(
        "Could not delete case. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return false;
    }
    _cases.removeWhere((caseModel) => caseModel.id == caseId);
    notifyListeners();
    return true;
  }

  Future<void> sortCases() async {
    _logger.warning("Unimplemented: sortCases()");
  }

  Future<void> filterCases() async {
    // Klasse FilterCriteria mit Feld fuer jedes Filterkriterium.
    // Aktuelle Filter werden durch Zustand einer FilterCriteria Instanz
    // definiert.
    _logger.warning("Unimplemented: filterCases()");
  }
}
