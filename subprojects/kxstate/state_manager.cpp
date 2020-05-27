#include "kx/state/state_manager.hpp"

#include "kx/state/state.hpp"

namespace kx::state
{
    StateManager::StateManager()
        : _current_state(nullptr)
        , _factory(nullptr)
    {}

    StateManager::StateManager(
        StateFactory * factory
    )
        : _current_state(nullptr)
        , _factory(factory)
    {}

    StateManager::~StateManager()
    {}

    void
    StateManager::switch_to_state(
        State * state
    )
    {
        if (_current_state != nullptr)
        {
            _current_state->on_leave();
        }
        _current_state = state;
        _current_state->on_enter();
    }
}
