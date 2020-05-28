#ifndef KX_STATE_STATE_MANAGER_HPP
#define KX_STATE_STATE_MANAGER_HPP

#include "kx/state/state_fwd.hpp"
#include "kx/state/state_factory_fwd.hpp"

namespace kx
{
namespace state
{
    class StateManager
    {
    public:
        StateManager();
        explicit StateManager(StateFactory * factory);
        virtual ~StateManager();

        virtual void switch_to_state(State * state);

        inline StateFactory * factory() { return _factory; }
    private:
        State           * _current_state;
        StateFactory    * _factory;
    };
}
}
#endif // KX_STATE_STATE_MANAGER_HPP
