# This file is executed on every boot (including wake-boot from deepsleep)

# Disable ESP Debug printing - incredibly annoying
import esp
esp.osdebug(None)

# Setup garbage collection
#import gc
#gc.collect()
