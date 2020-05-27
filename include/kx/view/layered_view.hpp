#include <list>

#include "kx/view/view.hpp"
#include "kx/view/layered_position.hpp"

namespace kx::view
{
    class Context;

    class LayeredView : public View
    {
    public:
        virtual void render(Context * context) const;
        virtual LayeredPosition * create_position();
    };
}
