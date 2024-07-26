#ifndef ITERABLEPREFERENCES_H
#define ITERABLEPREFERENCES_H

#include <nvs.h>
#include <Preferences.h>

class IterablePreferences : public Preferences {
public:
    IterablePreferences() = default;

    using Callback = void(const char* key, nvs_type_t type);
    void foreach (const char* nvNamespace, Callback cb, const char* nvPartition = "nvs") {
        nvs_iterator_t it = nvs_entry_find(nvPartition, nvNamespace, NVS_TYPE_ANY);
        while (it) {
            nvs_entry_info_t info{};
            nvs_entry_info(it, &info);  // Can omit error check if parameters are guaranteed to be non-NULL
            if (cb) {
                cb(info.key, info.type);
            }
            it = nvs_entry_next(it);
        }
        nvs_release_iterator(it);
    }
};

#endif ITERABLEPREFERENCES_H
