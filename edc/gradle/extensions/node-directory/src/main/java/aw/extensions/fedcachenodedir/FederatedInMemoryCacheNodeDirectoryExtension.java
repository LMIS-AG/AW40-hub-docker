package aw.extensions.fedcachenodedir;

import org.eclipse.edc.catalog.directory.InMemoryNodeDirectory;
import org.eclipse.edc.catalog.spi.FederatedCacheNode;
import org.eclipse.edc.catalog.spi.FederatedCacheNodeDirectory;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

import java.util.Collections;

public class FederatedInMemoryCacheNodeDirectoryExtension implements ServiceExtension {

    @Override
    public void initialize(ServiceExtensionContext context) {
        Monitor monitor = context.getMonitor();
        monitor.info("Init FCN Service Extension");

        FederatedCacheNodeDirectory federatedCacheNodeDirectory = new InMemoryNodeDirectory();
        FederatedCacheNode node1 = new FederatedCacheNode("Node 1", "http://192.168.0.41:8282/protocol", Collections.singletonList("dataspace-protocol-http"));

        federatedCacheNodeDirectory.insert(node1);

        context.registerService(FederatedCacheNodeDirectory.class, federatedCacheNodeDirectory);
    }

    @Override
    public void start() {

    }

    @Override
    public void shutdown() {

    }
}

