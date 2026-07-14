# @meganova/nova-os-client — DEPRECATED

This package has been **renamed to [`@libraos/client`](https://www.npmjs.com/package/@libraos/client)**.

LibraOS is the public brand; the Nova OS name is retired. This package now
re-exports `@libraos/client` unchanged, so existing imports keep working:

```ts
// still works (deprecated)
import { NovaClient } from "@meganova/nova-os-client";

// preferred
import { NovaClient } from "@libraos/client";
```

Please migrate your imports to `@libraos/client`. This alias will be kept for
backward compatibility but receives no new development.
