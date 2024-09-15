import "package:aw40_hub_frontend/models/customer_model.dart";
import "package:flutter_test/flutter_test.dart";

void main() {
  group("CostumerModel", () {
    const id = "some_id";

    final costumerModel = CustomerModel(
      id: id,
    );
    test("correctly assigns id", () {
      expect(costumerModel.id, id);
    });
  });
}
