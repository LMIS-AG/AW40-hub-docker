package query;

import java.util.List;

public class FederatedCacheNode {
    private String name;
    private String url;
    private List<String> protocols;


    public String getName() {
        return name;
    }
    public String getUrl() {
        return url;
    }
    public List<String> getProtocols() {
        return protocols;
    }

}
