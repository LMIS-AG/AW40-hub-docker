import "package:aw40_hub_frontend/models/costumer_model.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:flutter_test/flutter_test.dart";

void main() {
  group("CostumerModel", () {
    const id = AnonymousCustomerId.anonymous;

    final costumerModel = CostumerModel(
      id: id,
    );
    test("correctly assigns id", () {
      expect(costumerModel.id, id);
    });
  });
}
