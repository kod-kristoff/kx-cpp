project('bike-race-game', 'cpp')

inc_dir = include_directories('include')
sdl_dep = dependency('sdl')
sdl_ttf_dep = dependency('SDL_ttf')
sdl_image_dep = dependency('SDL_image')
executable(
  'bike_race_game',
  'src/main.cpp',
  include_directories: inc_dir,
  dependencies: [sdl_dep, sdl_ttf_dep, sdl_image_dep]
)
