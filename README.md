# crd-charts
Helm charts for managing of CRDs for common helm applications.

This is an attempt to ease the Helm / CRD management issue by creating charts that contain the CRDs
for various Helm charts. 

You can read more about the problem here: https://helm.sh/docs/chart_best_practices/custom_resource_definitions/

We have opted for [Method 2: Separate Charts](https://helm.sh/docs/chart_best_practices/custom_resource_definitions/#method-2-separate-charts).

## How does it work?

Charts are added to `helmfile.yaml` as releases (we're mis-using `helmfile` to make updates easy and visible), `helmfile` is used to fetch
the charts and run some hooks to create the crd charts and the charts are deployed to GitHub Pages (with GitHub Actions).

### Chart Names
The name of the CRDs chart for a Helm chart is:
```
$repo-$chartName-crds
```

For example, the CRDs chart for `cert-manager` chart in the `jetstack` Helm repository will have the name:
```
jetstack-cert-manager-crds
```

and can be installed by running:
```
helm repo add crd-charts https://portswigger-cloud.github.io/crd-charts/
helm install -n kube-=system jetstack-cert-manager-crds crd-charts/jetstack-cert-manager-crds
```

### Versions
The CRDs charts _should_ be versioned matching the Helm chart. Often, there will be no changes between versions.

There is the chance that a version may not be available due to the renovate automation to update CRD charts
(**There's no guarantee that a chart version will have been generated. check the releases on this repository**).

