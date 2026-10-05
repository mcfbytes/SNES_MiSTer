/* lrrun2 <core.so> <rom> <frames> <outdir> <script> <dumps>: lrrun plus pad-1 input spans ("a-b:keys", keys from
   BYsSudlrAXLR as in mklsmv.py) and a PPM of each frame listed in <dumps> (comma list, 0-based). */
#include <dlfcn.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "libretro.h"

static unsigned fmt = RETRO_PIXEL_FORMAT_0RGB1555, fw, fh;
static size_t fpitch;
static unsigned char frame[1024 * 1024 * 4];

static void logcb(enum retro_log_level l, const char *f, ...) {
  va_list a; va_start(a, f); vfprintf(stderr, f, a); va_end(a);
}
static bool env(unsigned cmd, void *d) {
  switch (cmd) {
  case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT: fmt = *(enum retro_pixel_format *)d; return true;
  case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY:
  case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY: *(const char **)d = "."; return true;
  case RETRO_ENVIRONMENT_GET_LOG_INTERFACE: ((struct retro_log_callback *)d)->log = logcb; return true;
  case RETRO_ENVIRONMENT_GET_CAN_DUPE: *(bool *)d = true; return true;
  case RETRO_ENVIRONMENT_GET_VARIABLE: {  /* LR_VARS="key=value,key=value" answers core options */
    struct retro_variable *v = d; const char *all = getenv("LR_VARS"); static char val[256];
    if (!all || !v->key) return false;
    size_t n = strlen(v->key);
    for (const char *q = all; (q = strstr(q, v->key)); q += n)
      if ((q == all || q[-1] == ',') && q[n] == '=') {
        size_t m = strcspn(q + n + 1, ","); if (m >= sizeof val) return false;
        memcpy(val, q + n + 1, m); val[m] = 0; v->value = val; return true;
      }
    return false;
  }
  default: if (getenv("LR_DEBUG")) fprintf(stderr, "env %u\n", cmd); return false;
  }
}
static void video(const void *p, unsigned w, unsigned h, size_t pitch) {
  if (!p) return;
  fw = w; fh = h; fpitch = pitch;
  memcpy(frame, p, pitch * h);
}
static void audio(int16_t l, int16_t r) {}
static size_t audio_batch(const int16_t *d, size_t n) { return n; }
static void poll(void) {}
static int cur; static int span_a[64], span_b[64]; static unsigned span_k[64]; static int nspan;
static int16_t input(unsigned port, unsigned dev, unsigned idx, unsigned id) {
  if (port != 0 || dev != RETRO_DEVICE_JOYPAD) return 0;
  for (int i = 0; i < nspan; i++) if (cur >= span_a[i] && cur < span_b[i] && (span_k[i] >> id & 1)) return 1;
  return 0;
}
static void parse(const char *sc) {
  const char *o = "BYsSudlrAXLR";
  char buf[4096]; strncpy(buf, sc, sizeof buf - 1);
  for (char *t = strtok(buf, ","); t && nspan < 64; t = strtok(NULL, ",")) {
    char keys[32] = ""; sscanf(t, "%d-%d:%31s", &span_a[nspan], &span_b[nspan], keys);
    for (char *k = keys; *k; k++) { const char *q = strchr(o, *k); if (q) span_k[nspan] |= 1u << (q - o); }
    nspan++;
  }
}
static void dump(const char *dir, int n);

#define SYM(n) n##_t n = (n##_t)dlsym(h, #n)
typedef void (*retro_init_t)(void);
typedef void (*retro_run_t)(void);
typedef bool (*retro_load_game_t)(const struct retro_game_info *);
typedef void *(*retro_get_memory_data_t)(unsigned);
typedef size_t (*retro_get_memory_size_t)(unsigned);
typedef void (*setenv_t)(retro_environment_t);

int main(int argc, char **argv) {
  if (argc < 5) return 2;
  void *h = dlopen(argv[1], RTLD_NOW);
  if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
  ((setenv_t)dlsym(h, "retro_set_environment"))(env);
  ((void (*)(retro_video_refresh_t))dlsym(h, "retro_set_video_refresh"))(video);
  ((void (*)(retro_audio_sample_t))dlsym(h, "retro_set_audio_sample"))(audio);
  ((void (*)(retro_audio_sample_batch_t))dlsym(h, "retro_set_audio_sample_batch"))(audio_batch);
  ((void (*)(retro_input_poll_t))dlsym(h, "retro_set_input_poll"))(poll);
  ((void (*)(retro_input_state_t))dlsym(h, "retro_set_input_state"))(input);
  SYM(retro_init); SYM(retro_run); SYM(retro_load_game); SYM(retro_get_memory_data); SYM(retro_get_memory_size);
  retro_init();
  FILE *f = fopen(argv[2], "rb");
  if (!f) return 1;
  static unsigned char rom[8 << 20];
  size_t n = fread(rom, 1, sizeof rom, f);
  fclose(f);
  struct retro_game_info gi = {argv[2], rom, n, NULL};
  if (!retro_load_game(&gi)) { fprintf(stderr, "load failed\n"); return 1; }
  if (argc > 5) parse(argv[5]);
  char dl[4096] = ","; if (argc > 6) { strncat(dl, argv[6], sizeof dl - 3); strcat(dl, ","); }
  for (cur = 0; cur < atoi(argv[3]); cur++) {
    retro_run();
    char key[32]; snprintf(key, sizeof key, ",%d,", cur);
    if (strstr(dl, key)) dump(argv[4], cur);
  }
  char p[4096];
  snprintf(p, sizeof p, "%s/wram.bin", argv[4]);
  f = fopen(p, "wb");
  fwrite(retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM), 1, retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM), f);
  fclose(f);
  fprintf(stderr, "fmt=%u w=%u h=%u pitch=%zu\n", fmt, fw, fh, fpitch);
  snprintf(p, sizeof p, "%s/last.ppm", argv[4]);
  f = fopen(p, "wb");
  fprintf(f, "P6 %u %u 255\n", fw, fh);
  for (unsigned y = 0; y < fh; y++)
    for (unsigned x = 0; x < fw; x++) {
      unsigned char rgb[3];
      if (fmt == RETRO_PIXEL_FORMAT_XRGB8888 || fpitch >= fw * 4) {
        unsigned v = *(unsigned *)(frame + y * fpitch + x * 4);
        rgb[0] = v >> 16; rgb[1] = v >> 8; rgb[2] = v;
      } else {
        unsigned v = *(unsigned short *)(frame + y * fpitch + x * 2);
        if (fmt == RETRO_PIXEL_FORMAT_RGB565) { rgb[0] = (v >> 11) << 3; rgb[1] = ((v >> 5) & 63) << 2; rgb[2] = (v & 31) << 3; }
        else { rgb[0] = ((v >> 10) & 31) << 3; rgb[1] = ((v >> 5) & 31) << 3; rgb[2] = (v & 31) << 3; }
      }
      fwrite(rgb, 1, 3, f);
    }
  fclose(f);
  return 0;
}
static void dump(const char *dir, int n) {
  char p[512]; snprintf(p, sizeof p, "%s/f%05d.ppm", dir, n);
  FILE *f = fopen(p, "wb");
  fprintf(f, "P6 %u %u 255\n", fw, fh);
  for (unsigned y = 0; y < fh; y++)
    for (unsigned x = 0; x < fw; x++) {
      unsigned char rgb[3];
      if (fmt == RETRO_PIXEL_FORMAT_XRGB8888 || fpitch >= fw * 4) {
        unsigned v = *(unsigned *)(frame + y * fpitch + x * 4);
        rgb[0] = v >> 16; rgb[1] = v >> 8; rgb[2] = v;
      } else {
        unsigned v = *(unsigned short *)(frame + y * fpitch + x * 2);
        if (fmt == RETRO_PIXEL_FORMAT_RGB565) { rgb[0] = (v >> 11) << 3; rgb[1] = ((v >> 5) & 63) << 2; rgb[2] = (v & 31) << 3; }
        else { rgb[0] = ((v >> 10) & 31) << 3; rgb[1] = ((v >> 5) & 31) << 3; rgb[2] = (v & 31) << 3; }
      }
      fwrite(rgb, 1, 3, f);
    }
  fclose(f);
}
