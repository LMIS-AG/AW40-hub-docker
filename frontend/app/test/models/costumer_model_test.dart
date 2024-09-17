import "package:aw40_hub_frontend/models/customer_model.dart";
import "package:flutter_test/flutter_test.dart";

void main() {
  group("CostumerModel", () {
    const id = "some_id";
    const firstname = "some_firstname";
    const lastname = "some_lastname";

    final costumerModel =
        CustomerModel(id: id, firstname: firstname, lastname: lastname);
    test("correctly assigns id", () {
      expect(costumerModel.id, id);
    });
    test("correctly assigns firstname", () {
      expect(costumerModel.firstname, firstname);
    });
    test("correctly assigns lastname", () {
      expect(costumerModel.lastname, lastname);
    });
  });
}
