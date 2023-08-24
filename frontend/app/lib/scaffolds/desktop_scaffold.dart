import "package:aw40_hub_frontend/components/components.dart";
import "package:aw40_hub_frontend/models/models.dart";
import "package:aw40_hub_frontend/utils/constants.dart";
import "package:flutter/material.dart";

class DesktopScaffold extends StatelessWidget {
  const DesktopScaffold({
    required this.navItems,
    required this.currentIndex,
    required this.onNavItemTap,
    required this.loggedInUserModel,
    required this.child,
    super.key,
  });

  final List<NavigationMenuItemModel> navItems;
  final int currentIndex;
  final void Function(int) onNavItemTap;
  final LoggedInUserModel loggedInUserModel;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final NavigationMenuItemModel navItem = navItems[currentIndex];
    final colorScheme = Theme.of(context).colorScheme;
    return Material(
      child: Scaffold(
        body: Row(
          children: [
            SizedBox(
              width: kDesktopSideMenuWidth,
              child: Card(
                margin: EdgeInsets.zero,
                shape: const RoundedRectangleBorder(
                  borderRadius: BorderRadius.horizontal(
                    right: Radius.circular(8),
                  ),
                ),
                color: colorScheme.surface,
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: Image.asset(kAssetAwLogoKlein),
                    ),
                    const Divider(),
                    Expanded(
                      child: ListView.builder(
                        itemBuilder: (c, i) {
                          final NavigationMenuItemModel navItem = navItems[i];
                          return ListTile(
                            leading: navItem.icon,
                            title: navItem.isExternal
                                ? Row(
                                    children: [
                                      Text(navItem.title),
                                      const SizedBox(width: 8),
                                      const Icon(Icons.open_in_new)
                                    ],
                                  )
                                : Text(navItem.title),
                            selected: i == currentIndex,
                            onTap: () => onNavItemTap(i),
                            selectedColor: colorScheme.secondary,
                          );
                        },
                        itemCount: navItems.length,
                      ),
                    ),
                    const Divider(),
                    ListTile(
                      dense: true,
                      leading: const CompanyAvatar(),
                      title: Text(loggedInUserModel.fullName),
                      trailing: const UserSettingsPopupButton(),
                    ),
                    const SizedBox(height: 8),
                  ],
                ),
              ),
            ),
            Expanded(
              child: Column(
                children: [
                  DesktopAppBar(
                    title: navItem.title,
                    actions: navItem.actions,
                  ),
                  Expanded(child: child),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
